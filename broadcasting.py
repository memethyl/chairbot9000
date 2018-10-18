import config
import discord
from discord.ext import commands
from misc import sendembed

class Broadcasting():
	def __init__(self, bot):
		self.bot = bot
	@commands.command(pass_context=True, description="Kick one or more users from the broadcast voice channel.")
	async def bkick(self, ctx, *users: discord.Member):
		"""Kicks one or more users from the broadcast voice channel."""
		try:
			kickchan = await self.bot.create_channel(ctx.message.server, 'Kicking...', type=discord.ChannelType.voice)
		except:
			content = "Couldn't kick {0} from the station; try again later!".format(', '.join([user.mention for user in users]))
			await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_red(),
							title="Failed to Kick", content=content)
			return
		for user in users:
			await self.bot.move_member(user, kickchan)
		await self.bot.delete_channel(kickchan)

		if len(users) > 1:
			content = "Users {0} kicked from the station".format(', '.join([user.mention for user in users]))
		else:
			content = "User {0} kicked from the station".format(users[0].mention)
		await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_green(),
						title="Kicked Successfully", content=content)
	@commands.group(pass_context=True)
	async def broadcast(self, ctx):
		"""&broadcast [add/remove/start/end] ..."""
		if ctx.invoked_subcommand is None:
			content = "Correct syntax: `&broadcast [add/remove/start/end] [@user1 @user2 for changing broadcasters / description for starting a broadcast]"
			await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_red(),
							title="Invalid command syntax", content=content)
	@broadcast.command(pass_context=True, description="Add a user as a broadcaster.")
	async def add(self, ctx, *users: discord.Member):
		"""Gives a user speaking privileges in the broadcast voice channel."""
		voicechan = discord.utils.get(ctx.message.server.channels, id=config.cfg["broadcasting"]["broadcast_vc"])
		broadcast_perm = discord.PermissionOverwrite()
		broadcast_perm.connect = True
		broadcast_perm.speak = True
		for user in users:
			await self.bot.edit_channel_permissions(voicechan, user, broadcast_perm)
			if ctx.message.author.voice_channel != None:
				self.bot.server_voice_state(user, mute=False)
			else:
				content = "Please manually unmute the broadcaster(s). You must be in the voice channel for automated unmute to work."
				await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_red(),
								title="Unable to Unmute", content=content)
	@broadcast.command(pass_context=True, description="Remove a broadcaster, turning them back into a listener.")
	async def remove(self, ctx, *users: discord.Member):
		"""Removes a user's speaking privileges in the broadcast voice channel."""
		voicechan = discord.utils.get(ctx.message.server.channels, id=config.cfg["broadcasting"]["broadcast_vc"])
		broadcast_perm = discord.PermissionOverwrite()
		broadcast_perm.connect = None
		broadcast_perm.speak = False
		for user in users:
			await self.bot.edit_channel_permissions(voicechan, user, broadcast_perm)
			if ctx.message.author.voice_channel != None:
				self.bot.server_voice_state(user, mute=True)
			else:
				content = "Please manually mute the broadcaster(s). You must be in the voice channel for automated mute to work."
				await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_red(),
								title="Unable to Mute", content=content)
	@broadcast.command(pass_context=True, description="Start a broadcast.")
	async def start(self, ctx, *, description: str="General Broadcast"):
		"""Sends a message in the configured broadcast announcement channel, and opens the configured voice channel for people to join."""
		voicechan = discord.utils.get(ctx.message.server.channels, id=config.cfg["broadcasting"]["broadcast_vc"])
		await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_green(),
						title="Broadcast Starting", content="Now starting a broadcast.")
		announcechan = discord.utils.get(ctx.message.server.channels, id=config.cfg["broadcasting"]["announce_channel"])
		content = ctx.message.author.mention + " has started a broadcast: \n\n" + description + \
				  "\n\nTo listen, join the Mum\'s Station voice channel. Please keep discussion to the automatically available home theater text channel."
		await sendembed(self.bot, channel=announcechan, color=discord.Colour.dark_green(),
						title="🎙 Broadcast Started", content=content, author=ctx.message.author)
		thonks = discord.utils.get(ctx.message.author.server.roles, name='thonks')
		thonks_perm = discord.PermissionOverwrite()
		thonks_perm.connect = True
		thonks_perm.speak = False
		await self.bot.edit_channel_permissions(voicechan, thonks, thonks_perm)
	@broadcast.command(pass_context=True, description="End a broadcast.")
	async def end(self, ctx):
		"""Announces that the broadcast has ended, and kicks all users out of the broadcast voice channel."""
		voicechan = discord.utils.get(ctx.message.server.channels, id=config.cfg["broadcasting"]["broadcast_vc"])
		if ctx.message.author.voice_channel is None or ctx.message.author.voice_channel != voicechan:
			content = "You must be in the broadcast voice channel to end the broadcast."
			await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_red(),
							title="Failed to End Broadcast", content=content)
		else:
			await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_red(),
							title="Ending Broadcast", content="Now ending the broadcast.")
			announcechan = discord.utils.get(ctx.message.server.channels, id=config.cfg["broadcasting"]["announce_channel"])
			thonks_perm.connect = False
			thonks_perm.speak = False
			await self.bot.edit_channel_permissions(voicechan, thonks, thonks_perm)
			disconnect = await self.bot.create_channel(server, 'Disconnecting...', type=discord.ChannelType.voice)
			for user in ctx.message.author.voice_channel.voice_members:
				await self.bot.move_member(user, disconnect)
			await self.bot.delete_channel(disconnect)
			content = "The broadcast has ended and all users have been disconnected. Thanks for listening!"
			await sendembed(self.bot, channel=announcechan, color=discord.Colour.dark_red(),
							title="🎙 Broadcast Ended", content=content)
		# clean up the permissions a bit
		vc_perms = voicechan.overwrites
		for item in vc_perms:
			if type(item[0]) is discord.Member:
				await self.bot.delete_channel_permissions(voicechan, item[0])
	@broadcast.command(pass_context=True, description="Alias for &broadcast end.")
	async def stop(self, ctx):
		"""(alias for &broadcast end)"""
		self.end(ctx)

def setup(bot):
	bot.add_cog(Broadcasting(bot))