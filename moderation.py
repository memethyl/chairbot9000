import discord
from math import floor
from discord.ext import commands
from misc import Config, sendembed
from os import remove
import pickle
save_config = Config.save_config
read_config = Config.read_config

class Moderation():
	def __init__(self, bot):
		self.bot = bot
		self.config = read_config()
	@commands.command(pass_context=True, description="Shuts down one or more channels to prevent thonks from typing in them.")
	async def shutdown(self, ctx, *channels: discord.Channel):
		"""Shuts down one or more channels, preventing thonks from talking in them."""
		# affected channels get pickled into a file, 
		# so that &restore can automatically restore whichever channel(s) you shut down
		channels_file = open('channels_shutdown.pkl', 'wb')
		if len(channels) != 0:
			thonks = discord.utils.get(ctx.message.author.server.roles, name='thonks')
			overwrite = discord.PermissionOverwrite()
			async for channel in channels:
				# casino_and_botspam
				if channel.id == '356816009778167809':
					overwrite.send_messages = True
				else:
					overwrite.send_messages = False
					overwrite.add_reactions = False
				await self.bot.edit_channel_permissions(channel, thonks, overwrite)
				content = 'Due to excessive chat activity, this text channel has been temporarily closed for all users.\n\nPlease wait for an admin to address the situation, and do not DM any staff in the meantime.'
				await sendembed(self.bot, channel=message.channel, color=discord.Colour.dark_red(),
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
		"""Restores any channels that were shut down before, allowing thonks to talk in them again."""
		try:
			channels_file = open('channels_shutdown.pkl', 'rb')
		except FileNotFoundError:
			return
		if len(channels) != 0:
			thonks = discord.utils.get(ctx.message.author.server.roles, name='thonks')
			overwrite = discord.PermissionOverwrite()
			async for channel in channels:
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
					# end of pickle file, stop restoring now
					pass
					
		channels_file.close()
		remove('channels_shutdown.pkl') # remove the file to tie up any loose ends
	@commands.command(pass_context=True, description="Purge a number of messages from a channel.")
	async def purge(self, ctx, amount: int):
		"""Purge a certain amount of messages from a channel."""
		amount += 1
		async for message in self.bot.logs_from(ctx.message.channel, amount):
			await self.bot.delete_message(message)
	@commands.command(pass_context=True, description="Permanently mute one or more users.")
	async def pmute(self, ctx, *users: discord.Member):
		"""Permanently mute one or more users."""
		muterole = discord.utils.get(ctx.message.author.server.roles, name='Muted')
		for user in users:
			await self.bot.add_roles(user, muterole)
		if len(users) > 1:
			content = 'Users '+''.join([user.mention for user in users])+' have been permanently muted.'
			await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_red(),
							title="Users Muted", content=content, author=ctx.message.author)
		else:
			content = 'User '+users[0].mention+' has been permanently muted.'
			await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_red(),
							title="User Muted", content=content, author=ctx.message.author)
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

def setup(bot):
	bot.add_cog(Moderation(bot))
