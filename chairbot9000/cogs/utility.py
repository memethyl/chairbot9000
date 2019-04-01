from   .           import config
import discord
from   discord.ext import commands
from   .misc       import sendembed
import os

class Utility(commands.Cog):
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
	# shamelessly stolen from https://gist.github.com/leovoel/46cd89ed6a8f41fd09c5
	@commands.command(description="Loads an extension.")
	async def load(ctx, extension_name: str):
		"""&load <extension name, usually cogs.X>"""
		try:
			ctx.load_extension(extension_name)
		except (AttributeError, ImportError) as e:
			await ctx.send(f"```py\n{type(e).__name__}: {str(e)}\n```")
			return
		await ctx.send(f"{extension_name} loaded.")
	@commands.command(description="Unloads an extension.")
	async def unload(ctx, extension_name: str):
		"""&unload <extension name, usually cogs.X>"""
		ctx.unload_extension(extension_name)
		await ctx.send(f"{extension_name} unloaded.")
	@commands.command(description="Set the mod role BY NAME for future permissions checks.\nNOTE: THIS MEANS ROLE MENTIONS WON'T WORK HERE")
	async def modset(self, ctx, rolename: str):
		"""&modset <name of desired role>"""
		if discord.utils.get(ctx.guild.roles, name=rolename) is None:
			content = f"Error: couldn't find role {rolename} in the server's roles!"
			await sendembed(channel=ctx.channel, color=discord.Colour.dark_red(),
							title="Unable to Set Mod Role", content=content)
		else:
			config.cfg["main"]["mod_role"] = rolename
			config.UpdateConfig.save_config(config.cfg)
			content = f"Mod role set to {rolename}."
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