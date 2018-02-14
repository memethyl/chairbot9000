try:
	tokenobject = open('tokenid.pkl', 'rb')
	tokenobject.close()
except FileNotFoundError:
	print("Error: tokenid.pkl not found; run setup.py first!")
	from sys import exit
	exit()

# this is for grabbing staticmethods from a class in another file
# since bot.add_extension won't grab them, you define them like so
from moderation import Moderation
from starboard import Starboard
from utility import Utility
membercheck = Moderation.membercheck 
post_starred = Starboard.post_starred 
handle_report = Utility.handle_report

import asyncio
import discord
import logging
from logging.handlers import RotatingFileHandler
import pickle
from discord.ext import commands
from misc import Config
read_config = Config.read_config

config = read_config()

# this allows discord.py to do automatic logging
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(filename=config["main"]["log_filepath"], encoding='utf-8', mode='w', \
							  maxBytes=config["main"]["max_log_size_bytes"], \
							  backupCount=config["main"]["log_backup_count"])
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
startup_extensions = ["moderation", "starboard", "broadcasting", "utility"]
# NOTE: PREFIX CANNOT BE CHANGED ON THE FLY; RESTART THE BOT IF YOU CHANGE THE PREFIX IN CONFIG.CFG
bot = commands.Bot(command_prefix=config["main"]["prefix"])
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
	print('------')

@bot.event
async def on_message(message):
	await bot.process_commands(message)

@bot.event
async def on_member_join(member):
	await membercheck(bot, config, member, server)

@bot.event
async def on_reaction_add(reaction, user):
	if reaction.emoji == config["starboard"]["emoji"]:
		await post_starred(bot, config, reaction, user)
	elif reaction.message.channel.id == config["reporting"]["report_channel"] and user.id != bot.user.id \
	and reaction.message.author.id == '204255221017214977': # 204255221017214977 is backup automum (YAGPDB.xyz#8760)
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
	if reaction.emoji == config["starboard"]["emoji"]:
		reacts = reaction.message.reactions
		# count the new amount of stars on a post
		starcount = None
		for react in reacts:
			if react.emoji == config["starboard"]["emoji"]:
				starlist = await bot.get_reaction_users(react)
				starcount = len(starlist)
				break
		starchan = bot.get_channel(config["starboard"]["star_channel"])
		# if the ID of the reaction's message is in the last 50 starboard posts,
		async for found_message in bot.logs_from(starchan, limit=50):
			if reaction.message.id in found_message.content:
				# edit that starboard post with the new number of stars
				new_content = config["starboard"]["emoji"] + ' ' + str(starcount) + ' ' + reaction.message.channel.mention + ' ID: ' + reaction.message.id
				await bot.edit_message(found_message, new_content=new_content)
				return

@bot.check
def check(ctx):
	"""Before running a command, check if that command was used in a channel the bot is listening to.
	Also, check if the user is a moderator.
	If either of those requirements aren't met, do nothing."""
	author_has_modrole = False
	for role in ctx.message.author.roles:
		if role.name == config["main"]["mod_role"]:
			author_has_modrole = True
	# note: because the modrole check is in here, all bot commands will be mod-only
	if ctx.message.channel.id not in config["main"]["listening_channels"] or not author_has_modrole:
		return False
	else:
		return True

if __name__ == "__main__":
	for extension in startup_extensions:
		try:
			bot.load_extension(extension)
		except Exception as e:
			exc = '{}: {}'.format(type(e).__name__, e)
			print('Failed to load extension {}\n{}'.format(extension, exc))
	try:
		tokenobject = open('tokenid.pkl', 'rb')
		tokenid = pickle.load(tokenobject)
		tokenobject.close()
		bot.run(tokenid)
	except discord.LoginFailure:
		print("Error: invalid token; run setup.py again, and make sure your token is correct!")
