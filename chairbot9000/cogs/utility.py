from   .           import config
import discord
from   discord.ext import commands
from   .misc       import sendembed
import os

class Utility():
	def __init__(self, bot):
		self.bot = bot
	@staticmethod
	async def handle_report(bot, message, reaction_emoji, user):
		"""Handle a report when a user has reacted to a YAGPDB report."""
		content = message.content
		if reaction_emoji == "✅":
			await sendembed(channel=message.channel, color=discord.Colour.dark_green(),
							title="✅ Action Taken", content=content, author=user)
		elif reaction_emoji == "🚫":
			await sendembed(channel=message.channel, color=discord.Colour.dark_red(),
							title="🚫 No Action Necessary", content=content, author=user)
		elif reaction_emoji == "⚠":
			await sendembed(channel=message.channel, color=discord.Colour.dark_red(),
							title="⚠ Troll Report", content=content, author=user)
		else:
			return
		await message.delete()
	@commands.command(description="Set the mod role BY NAME for future permissions checks.\nNOTE: THIS MEANS ROLE MENTIONS WON'T WORK HERE")
	async def modset(self, ctx, rolename: str):
		"""&modset <name of desired role>"""
		if discord.utils.get(ctx.guild.roles, name=rolename) is None:
			content = "Error: couldn't find role {0} in the server's roles!".format(rolename)
			await sendembed(channel=ctx.channel, color=discord.Colour.dark_red(),
							title="Unable to Set Mod Role", content=content)
		else:
			config.cfg["main"]["mod_role"] = rolename
			config.UpdateConfig.save_config(config.cfg)
			content = "Mod role set to {0}.".format(rolename)
			await sendembed(channel=ctx.channel, color=discord.Colour.dark_green(),
							title="Mod Role Set", content=content)
	@commands.command(description="Send a DM containing the bot's current config.")
	async def settings(self, ctx):
		"""&settings"""
		config_path = os.path.abspath(os.path.dirname(__file__))
		config_path = os.path.join(config_path, "../misc/config.cfg")
		config_file = open(config_path, 'rb')
		try:
			await ctx.author.send("Here's my current config.", file=discord.File(config_file))
		except:
			await ctx.channel.send("I couldn't send my config file! Make sure that I can DM you before trying again.")


def setup(bot):
	bot.add_cog(Utility(bot))