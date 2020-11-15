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
import os
import pickle
import sqlite3
import sys
import time
import traceback
config.init()

# if you change startup_extensions, make sure it stays in alphabetical order for convenience
startup_extensions = ['cogs.moderation', 'cogs.perms', 'cogs.starboard', 'cogs.utility']

class Chairbot9000(commands.Bot):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.add_check(self.perms_check)
		self.help_command = commands.DefaultHelpCommand(command_attrs={"aliases": ["h"]})
		for extension in startup_extensions:
			try:
				self.load_extension(extension)
			except Exception as e:
				exc = f"{type(e).__name__}: {e}"
				print(f"Failed to load extension {extension}\n{exc}")

	async def on_ready(self):
		import _version as v
		startup_info = [
			f"chairbot9000 v. {v.__version__} by memethyl#2461",
			f"Running as: {self.user.name}#{self.user.discriminator}",
			f"Started at: {datetime.now().strftime('%B %d, %Y %H:%M:%S')} ({datetime.utcnow().strftime('%B %d, %Y %H:%M:%S')} UTC)",
			f"Startup cogs: {', '.join(self.extensions.keys())}"
		]
		box_length = max([len(x) for x in startup_info])
		print("╔"+("═"*(box_length+2))+"╗")
		for item in startup_info:
			print("║ "+item+(" "*(abs(box_length-len(item))))+" ║")
		print("╚"+("═"*(box_length+2))+"╝")
		del startup_info, box_length, v

	async def on_message(self, message):
		# background tasks are basically impossible so this is the best i can do
		if not message.author.bot:
			await self.check_memed_users()
		# add reactions to report
		if message.author.id == 204255221017214977 and message.channel.id == config.cfg["reporting"]["report_channel"]:
								# YAGPDB.xyz#8760
			await message.add_reaction('✅') # action taken
			await message.add_reaction('🚫') # no action necessary
			await message.add_reaction('⚠') # troll report
		else:
			pass
		# alright now start processing commands or whatever
		await self.process_commands(message)

	async def on_member_join(self, member):
		await membercheck(bot, config.cfg, member, member.guild)

	async def on_raw_reaction_add(self, payload):
		channel = self.get_channel(payload.channel_id)
		try:
			message = await channel.fetch_message(payload.message_id)
		except discord.errors.NotFound:
			return
		user = await self.fetch_user(payload.user_id)
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

	async def on_raw_reaction_remove(self, payload):
		channel = self.get_channel(payload.channel_id)
		try:
			message = await channel.fetch_message(payload.message_id)
		except discord.errors.NotFound:
			return
		user = await self.fetch_user(payload.user_id)
		if payload.emoji.name == config.cfg["starboard"]["emoji"] and user != message.author:
			await post_starred(bot, config.cfg, message, payload.emoji.name, user)

	async def on_voice_state_update(self, member, before, after):
		vc_text = member.guild.get_channel(config.cfg["main"]["vc_text_channel"])
		if not before.channel and after.channel:
			await vc_text.set_permissions(member, read_messages=True, send_messages=True, reason="User joined voice channel")
		elif before.channel and not after.channel:
			await vc_text.set_permissions(member, overwrite=None, reason="User left voice channel")

	async def on_command_error(self, context, exception):
		if not context.valid:
			return
		print(f"Ignoring exception in command {context.invoked_with}", file=sys.stderr)
		traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)

	def perms_check(self, ctx):
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
	
	async def check_memed_users(self):
		meme_channel = discord.utils.get(self.get_all_channels(), id=config.cfg["moderation"]["meme_channel"])
		filedir = os.path.dirname(__file__)
		filedir = os.path.join(filedir, "misc/memed_users.db")
		conn = sqlite3.connect(filedir)
		c = conn.cursor()
		c.execute("SELECT * FROM memed_users")
		memed_users = c.fetchall()
		if memed_users != []:
			for user in memed_users[:]:
				if not self.get_user(user[0]):
					c.execute("DELETE FROM memed_users WHERE user_id=?", (user[0],))
					memed_users.remove(user)
				elif time.time() >= time.mktime(time.strptime(user[1], '%Y-%m-%d %H:%M:%S.%f')):
					await meme_channel.set_permissions(self.get_user(user[0]), overwrite=None, reason="Unbanning user from the meme channel")
					c.execute("DELETE FROM memed_users WHERE user_id=?", (user[0],))
					memed_users.remove(user)
		conn.commit()
		conn.close()

intents = discord.Intents(members=True, messages=True, reactions=True, guilds=True)
member_cache_flags = discord.MemberCacheFlags.from_intents(intents)
bot = Chairbot9000(command_prefix=config.cfg["main"]["prefix"], intents=intents, member_cache_flags=member_cache_flags)
tokenobject = open(token_path, 'rb')
tokenid = pickle.load(tokenobject)
tokenobject.close()
bot.run(tokenid)
