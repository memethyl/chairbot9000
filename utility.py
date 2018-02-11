import discord
from discord.ext import commands
from misc import Config, sendembed
import json
save_config = Config.save_config
read_config = Config.read_config

class Utility():
	def __init__(self, bot):
		self.bot = bot
		self.config = read_config()
	@staticmethod
	async def handle_report(bot, reaction, user):
		"""Handle a report when a user has reacted to a YAGPDB report."""
		content = reaction.message.content
		if reaction.emoji == "✅":
			await sendembed(bot, channel=reaction.message.channel, color=discord.Colour.dark_green(),
							title="✅ Action Taken", content=content, author=user)
		elif reaction.emoji == "🚫":
			await sendembed(bot, channel=reaction.message.channel, color=discord.Colour.dark_red(),
							title="🚫 No Action Necessary", content=content, author=user)
		elif reaction.emoji == "⚠":
			await sendembed(bot, channel=reaction.message.channel, color=discord.Colour.dark_red(),
							title="⚠ Troll Report", content=content, author=user)
		else:
			return
		await bot.delete_message(reaction.message)
	@commands.command(pass_context=True)
	async def modset(self, ctx, role: discord.Role):
		"""Set the moderator role BY NAME for future permissions checks."""
		self.config["main"]["mod_role"] = role.name
		self.config = save_config(self.config)
		content = "Mod role set to {0}.".format(role.name)
		await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_green(),
						title="Mod Role Set", content=content)
	@commands.command(pass_context=True)
	async def listen(self, ctx, channel: discord.Channel):
		"""Toggle whether or not the bot should listen to a channel."""
		if channel.id not in self.config["main"]["listening_channels"]:
			self.config["main"]["listening_channels"].append(channel.id)
			self.config = save_config(self.config)
			content = "Now listening to channel {0} for commands.".format(channel.mention)
			await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_red(),
							title="Now Listening To Channel", content=content)
		else:
			self.config["main"]["listening_channels"].remove(channel.id)
			self.config = save_config(self.config)
			content = "No longer listening to channel {0} for commands.".format(channel.mention)
			await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_red(),
							title="Stopped Listening To Channel", content=content)
	@commands.command(pass_context=True)
	async def settings(self, ctx):
		"""Sends a DM containing the bot's current config."""
		try:
			# send a DM containing the bot's current config
			await self.bot.send_message(ctx.message.author, '```json\n'+json.dumps(self.config, indent=4, sort_keys=True)+'\n```')
			# tell the user they've been sent a DM
			await self.bot.send_message(ctx.message.channel, "You have been sent a DM containing the bot's current config.")
		except discord.Forbidden:
			await self.bot.send_message(ctx.message.channel, "I was unable to send you a DM; make sure I can message you before running this command again!")

def setup(bot):
	bot.add_cog(Utility(bot))