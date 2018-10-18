import config
import discord
from discord.ext import commands
import json
from misc import sendembed

class Utility():
	def __init__(self, bot):
		self.bot = bot
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
	@commands.command(pass_context=True, description="Set the mod role BY NAME for future permissions checks.\nNOTE: THIS MEANS ROLE MENTIONS WON'T WORK HERE")
	async def modset(self, ctx, rolename: str):
		"""Set the moderator role BY NAME for future permissions checks."""
		if discord.utils.get(ctx.message.server.roles, name=rolename) is None:
			content = "Error: couldn't find role {0} in the server's roles!".format(rolename)
			await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_red(),
							title="Unable to Set Mod Role", content=content)
		else:
			config.cfg["main"]["mod_role"] = rolename
			config.UpdateConfig.save_config(config.cfg)
			content = "Mod role set to {0}.".format(rolename)
			await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_green(),
							title="Mod Role Set", content=content)
	@commands.command(pass_context=True, description="Send a DM containing the bot's current config.")
	async def settings(self, ctx):
		"""Sends a DM containing the bot's current config."""
		config_str = json.dumps(config.cfg, indent=4, sort_keys=True, ensure_ascii=False)
		# if the config is too big for one message,
		if len(config_str) > 1988: # (excluding the leading ```json\n and ending \n``` bits)
			# then send the DM piece by piece
			for i in range(0, len(config_str), 1988):
				try:
					await self.bot.send_message(ctx.message.author, '```json\n' + config_str[i:i+1988] + '\n```')
				except discord.Forbidden:
					await self.bot.send_message(ctx.message.channel, "I was unable to send you a DM; make sure I can message you before running this command again!")
					break
			else:
				await self.bot.send_message(ctx.message.channel, "You have been sent a DM containing the bot's current config.")
		else:
			try:
				# send a DM containing the bot's current config
				await self.bot.send_message(ctx.message.author, '```json\n' + config_str + '\n```')
				await self.bot.send_message(ctx.message.channel, "You have been sent a DM containing the bot's current config.")
			except discord.Forbidden:
				await self.bot.send_message(ctx.message.channel, "I was unable to send you a DM; make sure I can message you before running this command again!")


def setup(bot):
	bot.add_cog(Utility(bot))