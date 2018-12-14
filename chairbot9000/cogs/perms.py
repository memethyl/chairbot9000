from . import config
from discord.ext import commands
import discord
from .misc import sendembed

class Perms():
	def __init__(self, bot):
		self.bot = bot
	@commands.group()
	async def perms(self, ctx):
		"""&perms <set/remove> [...]"""
		if ctx.invoked_subcommand is None:
			content = "Correct syntax: `&perms <set/remove> [...]`"
			await sendembed(channel=ctx.channel, color=discord.Colour.dark_red(),
							title="Invalid command syntax", content=content)
	@perms.command(description="Set the required role for a certain command.")
	async def set(self, ctx, command: str, role: str):
		"""This does not check whether or not your desired command is valid.
			Do NOT type a command like "starboard set"; type "starboard" instead.
			All subcommands will have the same perms as their parents."""
		if command[0] is config.cfg["main"]["prefix"]: command = command[1:]
		role = discord.utils.get(ctx.guild.roles, name=role)
		if role:
			config.cfg["main"]["perms"][command] = role.id
			config.UpdateConfig.save_config(config.cfg)
			content = "Command "+command+" now requires the "+role.name+" role."
			await sendembed(channel=ctx.channel, color=discord.Colour.dark_green(),
							title="Permissions Changed", content=content)
		else:
			content = "Could not find that role."
			await sendembed(channel=ctx.channel, color=discord.Colour.dark_red(),
							title="Role Not Found", content=content)
	@perms.command(description="Remove a specific permission for a command, reverting it back to the default.")
	async def remove(self, ctx, command: str):
		"""This does not check whether or not your desired command is valid.
			However, this only works if your desired command actually has specific permissions in the first place."""
		if command[0] is config.cfg["main"]["prefix"]: command = command[1:]
		try:
			del config.cfg["main"]["perms"][command]
			config.UpdateConfig.save_config(config.cfg)
			content = "Perms for command "+command+" have been removed; command now uses default perms."
			await sendembed(channel=ctx.channel, color=discord.Colour.dark_green(),
							title="Permissions Removed", content=content)
		except KeyError:
			content = "Command "+command+" does not have specific permissions; check your spelling!"
			await sendembed(channel=ctx.channel, color=discord.Colour.dark_red(),
							title="Permissions Not Found", content=content)

def setup(bot):
	bot.add_cog(Perms(bot))