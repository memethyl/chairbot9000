import discord
from discord.ext import commands
from misc import Config, sendembed
save_config = Config.save_config
read_config = Config.read_config

class Memes():
	def __init__(self, bot):
		self.bot = bot
		self.config = read_config()
	@commands.group(pass_context=True, description="&memes [post/add/remove/list] ...")
	async def memes(self, ctx):
		"""&memes [post/add/remove/list] ..."""
		if ctx.invoked_subcommand is None:
			content = "Correct syntax: &memes [post/add/remove/list] ..."
			await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_red(),
							title="Invalid command syntax", content=content)
	@memes.command(pass_context=True, description="Post a specific meme to the current channel.")
	async def post(self, ctx, name: str):
		"""Post a meme to the channel the command was run in."""
		# this is "&memes post name" instead of "&memes name" because subcommands are weird
		try:
			await self.bot.send_message(ctx.message.channel, self.config["memes"][name])
		except KeyError:
			await self.bot.send_message(ctx.message.channel, "Error: copypasta `{0}` doesn't exist!".format(name))
	@memes.command(pass_context=True, description="Add a meme to the database, or change it if it already exists there.")
	async def add(self, ctx, name: str, *, copypasta: str):
		"""Add a meme to the database, or change an existing one."""
		if name not in self.config["memes"].keys():		
			self.config["memes"][name] = copypasta
			self.config = save_config(self.config)
			await self.bot.send_message(ctx.message.channel, "Copypasta `{0}` added.".format(name))
		else:
			self.config["memes"][name] = copypasta
			self.config = save_config(self.config)
			await self.bot.send_message(ctx.message.channel, "Copypasta `{0}` changed to `{1}`".format(name, copypasta[0:47]+'...'))
	@memes.command(pass_context=True, description="Remove a meme from the database.")
	async def remove(self, ctx, name: str):
		"""Remove a meme from the database."""
		try:
			self.config["memes"].pop(name)
			self.config = save_config(self.config)
			await self.bot.send_message(ctx.message.channel, "Copypasta `{0}` removed.".format(name))
		except KeyError:
			await self.bot.send_message(ctx.message.channel, "Error: copypasta `{0}` doesn't exist!".format(name))
	@memes.command(pass_context=True, description="Show the command for every meme in the database, along with a short preview of the output.")
	async def list(self, ctx):
		"""Show the command for each meme in the database, along with a short preview of the output."""
		content = """"""
		for name in self.config["memes"].keys():
			if len(self.config["memes"][name]) > 50:
				copypasta = (self.config["memes"][name][0:47]+'...').replace('\n', '\\n')
			else:
				copypasta = self.config["memes"][name]
			content += "`&memes post {0}` - `{1}`\n".format(name, copypasta)
		await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.gold(),
						title="Memes/Copypastas", content=content)

def setup(bot):
	bot.add_cog(Memes(bot))