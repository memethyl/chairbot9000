try:
	import os
	token_path = os.path.abspath(os.path.dirname(__file__))
	token_path = os.path.join(token_path, "misc/tokenid.pkl")
	tokenobject = open(token_path, 'rb')
	tokenobject.close()
	del os
except FileNotFoundError:
	print("Error: tokenid.pkl not found; run setup.py first!")
	from sys import exit
	exit()

# this is for grabbing staticmethods from a class in another file
# since bot.add_extension won't grab them, you define them like so
from cogs.moderation import Moderation
from cogs.starboard  import Starboard
from cogs.utility    import Utility
membercheck = Moderation.membercheck 
post_starred = Starboard.post_starred 
handle_report = Utility.handle_report

import asyncio
import cogs.config as     config
from   cogs.misc   import sendembed
from   datetime    import datetime
from   discord.ext import commands
import discord
import pickle
import sys, traceback
config.init()

# if you change startup_extensions, make sure it stays in alphabetical order for convenience
startup_extensions = ['cogs.memes', 'cogs.moderation', 'cogs.perms', 'cogs.starboard', 'cogs.utility']
# NOTE: PREFIX CANNOT BE CHANGED ON THE FLY; RESTART THE BOT IF YOU CHANGE THE PREFIX IN CONFIG.CFG
bot = commands.Bot(command_prefix=config.cfg["main"]["prefix"])

# shamelessly stolen from https://gist.github.com/leovoel/46cd89ed6a8f41fd09c5
@bot.command()
async def load(ctx, extension_name: str):
	"""Loads an extension."""
	try:
		bot.load_extension(extension_name)
	except (AttributeError, ImportError) as e:
		await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
		return
	await ctx.send("{} loaded.".format(extension_name))
@bot.command()
async def unload(ctx, extension_name: str):
	"""Unloads an extension."""
	bot.unload_extension(extension_name)
	await ctx.send("{} unloaded.".format(extension_name))

@bot.event
async def on_ready():
	import _version as v
	startup_info = [
		"chairbot9000 v. {} by memethyl#2461".format(v.__version__),
		"Running as: {}#{}".format(bot.user.name, bot.user.discriminator),
		"Started at: {} ({} UTC)".format(datetime.now().strftime("%B %d, %Y %H:%M:%S"), datetime.utcnow().strftime("%B %d, %Y %H:%M:%S")),
		"Startup cogs: {}".format(', '.join(bot.extensions.keys()))
	]
	box_length = max([len(x) for x in startup_info])
	print("╔"+("═"*(box_length+2))+"╗")
	for item in startup_info:
		print("║ "+item+(" "*(abs(box_length-len(item))))+" ║")
	print("╚"+("═"*(box_length+2))+"╝")
	del startup_info, box_length, v

@bot.event
async def on_message(message):
	# add reactions to report
	if message.author.id == 204255221017214977 and message.channel.id == config.cfg["reporting"]["report_channel"]:
							 # YAGPDB.xyz#8760
		await message.add_reaction('✅') # action taken
		await message.add_reaction('🚫') # no action necessary
		await message.add_reaction('⚠') # troll report
	else:
		pass
	# alright now start processing commands or whatever
	await bot.process_commands(message)

@bot.event
async def on_member_join(member):
	await membercheck(bot, config.cfg, member, member.guild)

@bot.event
async def on_raw_reaction_add(payload):
	channel = bot.get_channel(payload.channel_id)
	message = await channel.get_message(payload.message_id)
	user = await bot.get_user_info(payload.user_id)
	if payload.emoji.name == config.cfg["starboard"]["emoji"]:
		await post_starred(bot, config.cfg, message, payload.emoji.name, user)
	elif payload.channel_id == config.cfg["reporting"]["report_channel"] and user.bot is False \
	and message.author.id == 204255221017214977:
		await handle_report(bot, message, payload.emoji.name, user)
	# remove shrugs from pollbot polls
	elif payload.emoji.name == '🤷' and 'poll:' in message.content:
		reactors = [x.users() for x in message.reactions if x.emoji == '🤷'][0]
		async for user in reactors:
			await message.remove_reaction(payload.emoji, user)
	else:
		pass

@bot.event
async def on_raw_reaction_remove(payload):
	channel = bot.get_channel(payload.channel_id)
	message = await channel.get_message(payload.message_id)
	user = await bot.get_user_info(payload.user_id)
	if payload.emoji.name == config.cfg["starboard"]["emoji"] and user != message.author:
		await post_starred(bot, config.cfg, message, payload.emoji.name, user)

@bot.event
async def on_command_error(context, exception):
	if not context.valid:
		return
	print('Ignoring exception in command {}'.format(context.invoked_with), file=sys.stderr)
	traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)

@bot.check
def check(ctx):
	"""Before running a command, do a permissions check.
	If the user doesn't have the right role for the command, do nothing."""
	command = ctx.invoked_with
	try:
		if config.cfg["main"]["perms"][command] in [x.id for x in ctx.author.roles]:
			return True
		return False
	except KeyError:
		if config.cfg["main"]["perms"]["global"] in [x.id for x in ctx.author.roles]:
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
		tokenobject = open(token_path, 'rb')
		tokenid = pickle.load(tokenobject)
		tokenobject.close()
		bot.run(tokenid)
	except discord.LoginFailure:
		print("Error: invalid token; run setup.py again, and make sure your token is correct!")
	except KeyboardInterrupt:
		bot.close()
		print("Logged out at {0} UTC".format(datetime.utcnow()))