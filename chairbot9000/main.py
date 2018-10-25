try:
	tokenobject = open('misc/tokenid.pkl', 'rb')
	tokenobject.close()
except FileNotFoundError:
	print("Error: tokenid.pkl not found; run setup.py first!")
	from sys import exit
	exit()

# this is for grabbing staticmethods from a class in another file
# since bot.add_extension won't grab them, you define them like so
from cogs.moderation import Moderation
from cogs.starboard import Starboard
from cogs.utility import Utility
membercheck = Moderation.membercheck 
post_starred = Starboard.post_starred 
handle_report = Utility.handle_report

from aiohttp.errors import ClientOSError
from asyncio import CancelledError
import asyncio
import cogs.config as config
config.init()
from cogs.misc import sendembed
from datetime import datetime
from discord.ext import commands
import discord
import pickle

# if you change startup_extensions, make sure it stays in alphabetical order for convenience
startup_extensions = ['cogs.broadcasting', 'cogs.memes', 'cogs.moderation', 'cogs.perms', 'cogs.starboard', 'cogs.utility']
# NOTE: PREFIX CANNOT BE CHANGED ON THE FLY; RESTART THE BOT IF YOU CHANGE THE PREFIX IN CONFIG.CFG
bot = commands.Bot(command_prefix=config.cfg["main"]["prefix"])
server = bot.get_server('214249708711837696')

# shamelessly stolen from https://gist.github.com/leovoel/46cd89ed6a8f41fd09c5
@bot.command()
async def load(extension_name: str):
	"""Loads an extension."""
	try:
		bot.load_extension(extension_name)
	except (AttributeError, ImportError) as e:
		await bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
		return
	await bot.say("{} loaded.".format(extension_name))
@bot.command()
async def unload(extension_name: str):
	"""Unloads an extension."""
	bot.unload_extension(extension_name)
	await bot.say("{} unloaded.".format(extension_name))

@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print('at {0} UTC'.format(datetime.utcnow()))
	print('------')

@bot.event
async def on_message(message):
	# add reactions to report
	if message.author.id == '204255221017214977' and message.channel.id == config.cfg["reporting"]["report_channel"]: 
							 # YAGPDB.xyz#8760
		await bot.add_reaction(message, '✅') # action taken
		await bot.add_reaction(message, '🚫') # no action necessary
		await bot.add_reaction(message, '⚠') # troll report
	else:
		pass
	# alright now start processing commands or whatever
	await bot.process_commands(message)

@bot.event
async def on_member_join(member):
	await membercheck(bot, config.cfg, member, server)

@bot.event
async def on_reaction_add(reaction, user):
	if reaction.emoji == config.cfg["starboard"]["emoji"]:
		await post_starred(bot, config.cfg, reaction, user)
	elif reaction.message.channel.id == config.cfg["reporting"]["report_channel"] and user.bot is False \
	and reaction.message.author.id == '204255221017214977':
		await handle_report(bot, reaction, user)
	# remove shrugs from pollbot polls
	elif reaction.emoji == '🤷' and 'poll:' in reaction.message.content:
		reactors = await bot.get_reaction_users(reaction)
		for user in reactors:
			await bot.remove_reaction(reaction.message, reaction.emoji, user)
	else:
		pass

@bot.event
async def on_reaction_remove(reaction, user):
	if reaction.emoji == config.cfg["starboard"]["emoji"]:
		reacts = reaction.message.reactions
		# count the new amount of stars on a post
		starcount = None
		for react in reacts:
			if react.emoji == config.cfg["starboard"]["emoji"]:
				starlist = await bot.get_reaction_users(react)
				starcount = len(starlist)
				break
		starchan = bot.get_channel(config.cfg["starboard"]["star_channel"])
		# if the ID of the reaction's message is in the last 50 starboard posts,
		async for found_message in bot.logs_from(starchan, limit=50):
			if reaction.message.id in found_message.content:
				# edit that starboard post with the new number of stars
				new_content = config.cfg["starboard"]["emoji"] + ' ' + str(starcount) + ' ' + reaction.message.channel.mention + ' ID: ' + reaction.message.id
				await bot.edit_message(found_message, new_content=new_content)
				return

@bot.check
def check(ctx):
	"""Before running a command, do a permissions check.
	If the user doesn't have the right role for the command, do nothing."""
	command = ctx.invoked_with
	try:
		if config.cfg["main"]["perms"][command] in [x.name for x in ctx.message.author.roles]:
			return True
		return False
	except KeyError:
		if config.cfg["main"]["perms"]["global"] in [x.name for x in ctx.message.author.roles]:
			return True
		return False

if __name__ == "__main__":
	try:
		for extension in startup_extensions:
			try:
				bot.load_extension(extension)
			except Exception as e:
				exc = '{}: {}'.format(type(e).__name__, e)
				print('Failed to load extension {}\n{}'.format(extension, exc))
		tokenobject = open('misc/tokenid.pkl', 'rb')
		tokenid = pickle.load(tokenobject)
		tokenobject.close()
		bot.run(tokenid)
	except discord.LoginFailure:
		print("Error: invalid token; run setup.py again, and make sure your token is correct!")
	except KeyboardInterrupt:
		bot.close()
		print("Logged out at {0} UTC".format(datetime.utcnow()))