from asyncio import sleep
from . import config
from discord.ext import commands
import discord
from math import floor
from .misc import sendembed
from os import remove
import os
import pickle
import re

class Moderation():
	def __init__(self, bot):
		self.bot = bot
	@commands.command(pass_context=True, description="Shuts down one or more channels to prevent thonks from typing in them.")
	async def shutdown(self, ctx, *channels: discord.Channel):
		# affected channels get pickled into a file, 
		# so that &restore can automatically restore whichever channel(s) you shut down
		try:
			filedir = os.path.dirname(__file__)
			filedir = os.path.join(filedir, "../misc/channels_shutdown.pkl")
			channels_file = open(filedir, 'wb')
		except FileNotFoundError:
			filedir = os.path.dirname(__file__)
			filedir = os.path.join(filedir, "../misc/channels_shutdown.pkl")
			channels_file = open(filedir, 'x+b')
		if len(channels) != 0:
			thonks = discord.utils.get(ctx.message.author.server.roles, name='thonks')
			overwrite = discord.PermissionOverwrite()
			for channel in channels:
				# casino_and_botspam
				if channel.id == '356816009778167809':
					overwrite.send_messages = True
				else:
					overwrite.send_messages = False
					overwrite.add_reactions = False
				await self.bot.edit_channel_permissions(channel, thonks, overwrite)
				content = 'Due to excessive chat activity, this text channel has been temporarily closed for all users.\n\nPlease wait for an admin to address the situation, and do not DM any staff in the meantime.'
				await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_red(),
								title='🚫 Raid/spam protection has shut this channel down', content=content)
				pickle.dump(channel, channels_file)
		else:
			# shut down the channel the message was sent in
			channel = ctx.message.channel
			thonks = discord.utils.get(ctx.message.author.server.roles, name='thonks')
			overwrite = discord.PermissionOverwrite()
			if channel.id == '356816009778167809':
				overwrite.send_messages = True
			else:
				overwrite.send_messages = False
				overwrite.add_reactions = False
			await self.bot.edit_channel_permissions(channel, thonks, overwrite)
			content = 'Due to excessive chat activity, this text channel has been temporarily closed for all users.\n\nPlease wait for an admin to address the situation, and do not DM any staff in the meantime.'
			await sendembed(self.bot, channel=channel, color=discord.Colour.dark_red(),
							title='🚫 Raid/spam protection has shut this channel down', content=content)
			pickle.dump(channel, channels_file)
		channels_file.close()
	@commands.command(pass_context=True, description="Restores any channels that were shut down, allowing thonks to type in them again.")
	async def restore(self, ctx, *channels: discord.Channel):
		try:
			filedir = os.path.dirname(__file__)
			filedir = os.path.join(filedir, "../misc/channels_shutdown.pkl")
			channels_file = open(filedir, 'r+b')
		except FileNotFoundError:
			await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_red(),
							title="No Channels Shutdown", content="It doesn't seem like any channels were ever shut down.")
			return
		if len(channels) != 0:
			thonks = discord.utils.get(ctx.message.author.server.roles, name='thonks')
			overwrite = discord.PermissionOverwrite()
			for channel in channels:
				overwrite.send_messages = True
				overwrite.add_reactions = True
				await self.bot.edit_channel_permissions(channel, thonks, overwrite)
				content = 'The situation has been handled and this channel has been reopened.\n\nPlease do not spam messages asking what happened -- refer to the information in #announcements.'
				await sendembed(self.bot, channel=channel, color=discord.Colour.dark_green(),
								title='✅ Raid/spam protection has been lifted on this channel', content=content)
		else:
			while True:
				try:
					channel = pickle.load(channels_file)
					thonks = discord.utils.get(ctx.message.author.server.roles, name='thonks')
					overwrite = discord.PermissionOverwrite()
					overwrite.send_messages = True
					overwrite.add_reactions = True
					await self.bot.edit_channel_permissions(channel, thonks, overwrite)
					content = 'The situation has been handled and this channel has been reopened.\n\nPlease do not spam messages asking what happened -- refer to the information in #announcements.'
					await sendembed(self.bot, channel=channel, color=discord.Colour.dark_green(),
									title='✅ Raid/spam protection has been lifted on this channel', content=content)
				except EOFError:
					channel = ctx.message.channel
					thonks = discord.utils.get(ctx.message.author.server.roles, name='thonks')
					overwrite = discord.PermissionOverwrite()
					overwrite.send_messages = True
					overwrite.add_reactions = True
					await self.bot.edit_channel_permissions(channel, thonks, overwrite)
					content = 'The situation has been handled and this channel has been reopened.\n\nPlease do not spam messages asking what happened -- refer to the information in #announcements.'
					await sendembed(self.bot, channel=channel, color=discord.Colour.dark_green(),
									title='✅ Raid/spam protection has been lifted on this channel', content=content)
				break
		channels_file.close()
		remove(filedir) # remove the file to tie up any loose ends
	@commands.command(pass_context=True, description="Purge a certain amount of messages from a channel.")
	async def purge(self, ctx, amount: int):
		amount += 1
		async for message in self.bot.logs_from(ctx.message.channel, amount):
			await self.bot.delete_message(message)
			await sleep(0.5) # ratelimit shit idk
	@commands.command(pass_context=True, description="Permanently mute one or more users.")
	async def pmute(self, ctx, *users: discord.Member):
		muterole = discord.utils.get(ctx.message.author.server.roles, name='Muted')
		for user in users:
			await self.bot.add_roles(user, muterole)
		if len(users) > 1:
			content = 'Users '+''.join([user.mention for user in users])+' have been permanently muted.'
			await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_red(),
							title="Users Muted", content=content, author=ctx.message.author)
		elif len(users) == 1:
			content = 'User '+users[0].mention+' has been permanently muted.'
			await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_red(),
							title="User Muted", content=content, author=ctx.message.author)
		else:
			content = "Correct syntax: &pmute @user1 [@user2] [...]"
			await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_red(),
							title="Invalid command syntax", content=content)
	@commands.command(pass_context=True, description="Ban multiple IDs at once. Do NOT ping users in this command.")
	async def multiban(self, ctx, *users: str):
		content = "Please provide a ban reason. (for no ban reason, reply \"none\"; to abort, reply \"abort\")"
		await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.gold(),
						title="Optional Ban Reason", content=content)
		reason = await self.bot.wait_for_message(timeout=10, author=ctx.message.author, channel=ctx.message.channel)
		if reason is not None and reason.content.lower() == "abort":
			await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_red(),
							title="Aborting Multiban", content="Multiban aborted.")
			return
		else:
			if reason is None or reason.content.lower() == "none":
				reason = "No reason provided."
				await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.gold(),
								title="No Ban Reason Given", content="No reply received; continuing without a ban reason.")
			failed_bans = []
			successful_bans = []
			for user in users:
				try:
					user_object = await self.bot.get_user_info(user)
					await self.bot.ban(user_object)
					successful_bans.append(user)
				except discord.errors.NotFound:
					failed_bans.append(user)
			if len(successful_bans) == 0:
				content = "No users successfully banned"
			else:
				content = "Successfully banned users {0}".format(''.join(["`"+x+"`, " for x in users if x not in failed_bans]))
				if len(failed_bans) > 0:
					content += "\nFailed to ban users {0}".format(''.join(["`"+x+"`, " for x in failed_bans]))
			await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_green(),
							title="{0} Successful Bans, {1} Failed Bans".format(len(successful_bans), len(failed_bans)),
							content=content)
	@staticmethod
	async def membercheck(bot, config, member, server):
		"""Check the difference between a member's account creation time and their join time.
		   If the delta between those two is less than the autoban amount in config.cfg,
		   ban the member and leave a reason why in the appropriate channel."""
		join_time = member.joined_at
		creation_time = member.created_at
		delta = join_time - creation_time
		delta = delta.total_seconds()
		if delta/60 <= config["automod"]["autoban_mins"]:
			await bot.ban(member)
			hours = floor(delta/3600)
			minutes = floor((delta/60)%60)
			seconds = delta - (hours*3600) - (minutes*60)
			if config["automod"]["autoban_mins"] >= 60:
				deltastr = "{0} hours {1} minutes {2} seconds".format(hours, minutes, seconds)
			else:
				deltastr = "{0} minutes {1} seconds".format(minutes, seconds)
			content = "Banned {0} for being a new account\nAccount created at: {1}\nAccount joined at: {2}\nDelta: {3}".format(\
						member.mention, creation_time.strftime("%Y-%m-%d %H:%M:%S"), join_time.strftime("%Y-%m-%d %H:%M:%S"), \
						deltastr)
			channel = bot.get_channel(config["automod"]["banlog_channel"])
			await sendembed(bot, channel=channel, color=discord.Colour.gold(),
							title="⚠️ Newly Created Account Banned", content=content)
		# invite bots :ree:
		invite_regex = config["automod"]["invite_regex"]
		if re.search(invite_regex, str(member.name)) or re.search(invite_regex, str(member.nick)):
			await bot.ban(member)
			content = "Banned {0} for being a fucking invite bot".format(member.mention)
			channel = bot.get_channel(config["automod"]["banlog_channel"])
			await sendembed(bot, channel=channel, color=discord.Colour.gold(),
							title="⚠️ Invite Bot Banned ⚠️", content=content)

def setup(bot):
	bot.add_cog(Moderation(bot))
