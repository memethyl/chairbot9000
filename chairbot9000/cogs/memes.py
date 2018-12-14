from . import config
import discord
from discord.ext import commands
from .misc import sendembed

class Memes():
	def __init__(self, bot):
		self.bot = bot
	@commands.group()
	async def memes(self, ctx):
		"""&memes <post/add/remove/list> [...]"""
		if ctx.invoked_subcommand is None:
			content = "Correct syntax: `&memes <post/add/remove/list> [...]`"
			await sendembed(channel=ctx.channel, color=discord.Colour.dark_red(),
							title="Invalid command syntax", content=content)
	@memes.command(description="Post a meme to the channel the command was run in.")
	async def post(self, ctx, name: str):
		# this is "&memes post name" instead of "&memes name" because subcommands are weird
		try:
			await ctx.channel.send(config.cfg["memes"][name])
		except KeyError:
			await ctx.channel.send("Error: copypasta `{0}` doesn't exist!".format(name))
	@memes.command(description="Add a meme to the database, or change an existing one.")
	async def add(self, ctx, name: str, *, copypasta: str):
		if name not in config.cfg["memes"].keys():		
			config.cfg["memes"][name] = copypasta
			config.UpdateConfig.save_config(config.cfg)
			await ctx.channel.send("Copypasta `{0}` added.".format(name))
		else:
			config.cfg["memes"][name] = copypasta
			config.UpdateConfig.save_config(config.cfg)
			await ctx.channel.send("Copypasta `{0}` changed to `{1}`".format(name, copypasta[0:47]+'...'))
	@memes.command(description="Remove a meme from the database.")
	async def remove(self, ctx, name: str):
		try:
			config.cfg["memes"].pop(name)
			config.UpdateConfig.save_config(config.cfg)
			await ctx.channel.send("Copypasta `{0}` removed.".format(name))
		except KeyError:
			await ctx.channel.send("Error: copypasta `{0}` doesn't exist!".format(name))
	@memes.command(description="Show the command for every meme in the database, along with a short preview of the output.")
	async def list(self, ctx):
		content = """"""
		for name in config.cfg["memes"].keys():
			if len(config.cfg["memes"][name]) > 50:
				copypasta = (config.cfg["memes"][name][0:47]+'...').replace('\n', '\\n')
			else:
				copypasta = config.cfg["memes"][name]
			content += "`&memes post {0}` - `{1}`\n".format(name, copypasta)
		await sendembed(channel=ctx.channel, color=discord.Colour.gold(),
						title="Memes/Copypastas", content=content)

def setup(bot):
	bot.add_cog(Memes(bot))