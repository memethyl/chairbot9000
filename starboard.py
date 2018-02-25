import asyncio
import datetime
import discord
from discord.ext import commands
import json
import re
from misc import Config, sendembed
save_config = Config.save_config
read_config = Config.read_config

class Starboard():
	def __init__(self, bot):
		self.bot = bot
		self.config = read_config()
	@commands.group(pass_context=True, description="&starboard [set/num] [channel/minimum stars]")
	async def starboard(ctx):
		"""&starboard [set/num] ..."""
		if ctx.invoked_subcommand is None:
			content = "Correct syntax: `&starboard [set/num] [channel/minimum stars]"
			await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_red(),
							title="Invalid command syntax", content=content)
	@starboard.command(pass_context=True, description="Set the channel that starboard messages should be posted in.")
	async def set(self, ctx, channel: discord.Channel):
		"""Subcommand of starboard that sets the channel starboard messages should be posted in."""
		if channel:
			self.config["starboard"]["star_channel"] = channel.id
			self.config = save_config(self.config)
			content = "Starboard channel set to {0}.".format(channel.mention)
			await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_green(),
							title="Starboard Channel Set")
		else:
			content = "Correct syntax: `&starboard set [channel]"
			await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_red(),
							title="Invalid command syntax", content=content)
	@starboard.command(pass_context=True, description="Set the number of stars required for a post to go on the board.")
	async def num(self, ctx, amount: int):
		"""Subcommand of starboard that sets the number of stars a post needs to make it on the board."""
		if amount == 0: amount = 1
		self.config["starboard"]["star_amount"] = amount
		self.config = save_config(self.config)
		content = "Required amount of stars set to {0}.".format(str(amount))
		await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_green(),
						title="Star Amount Set", content=content)
	@commands.command(pass_context=True, description="Set whether or not moderators can override the star requirement.\n(to set the mod role, see &modset)")
	async def modstar(self, ctx, value: str):
		"""Sets whether or not moderators are able to override the star amount requirement."""
		if value.lower() == 'true' or value.lower() == 'false':
			self.config["starboard"]["mod_override"] = value.lower()
			self.config = save_config(self.config)
			content = "Mod star override set to {0}.".format(value.lower())
			color = discord.Colour.dark_green() if value.lower() == 'true' else discord.Colour.dark_red()
			await sendembed(self.bot, channel=ctx.message.channel, color=color,
							title="Mod Star Override Set", content=content)
		else:
			content = "Correct syntax: `&modstar [true/false]`"
			await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_red(),
							title="Invalid command syntax", content=content)
	@staticmethod
	async def post_starred(bot, config, reaction, user):
		def modcheck(bot, config, user):
			server = bot.get_server('214249708711837696')
			member = server.get_member(user.id)
			for role in member.roles:
				if role.name == config["main"]["mod_role"]:
					return True
			return False
		"""Checks a message's star count. If the star count meets or exceeds the amount required, put the message on the board."""
		# check new reactions to see if a post got the required amount of stars
		reacts = reaction.message.reactions
		mod_starred = False
		starlist = None
		starcount = None
		for react in reacts:
			if react.emoji == config["starboard"]["emoji"]:
				starlist = await bot.get_reaction_users(react)
				starcount = len(starlist)
				break
		else:
			return
		for reactor in starlist:
			if modcheck(bot, config, reactor):
				mod_starred = True
				break
		if reaction.message.author in starlist:
			selfstar_alert = '🚨 🚨 ' + reaction.message.author.mention + ' IS A THOT AND SELF-STARRED THEIR MEME 🚨 🚨'
			await bot.send_message(reaction.message.channel, selfstar_alert)
			await bot.remove_reaction(reaction.message, reaction.emoji, reaction.message.author)
			return
		# if starcount is greater than required (or a mod starred it and override is enabled), and the message being starred isn't from the bot,
		if (starcount >= config["starboard"]["star_amount"] or (mod_starred and config["starboard"]["mod_override"] == 'true')) \
		and reaction.message.author.id != bot.user.id:
			# start posting
			starchan = bot.get_channel(config["starboard"]["star_channel"])
			async for found_message in bot.logs_from(starchan, limit=50):
				# if the ID of the starred message was in any of the last 50 starboard posts,
				if reaction.message.id in found_message.content:
					# edit the message on the board with the new star count
					new_content = config["starboard"]["emoji"] + ' ' + str(starcount) + ' ' + reaction.message.channel.mention + ' ID: ' + reaction.message.id
					await bot.edit_message(found_message, new_content=new_content)
					return
			embed = discord.Embed(color=discord.Colour.gold(), description=reaction.message.content)
			name = reaction.message.author.name + '#' + reaction.message.author.discriminator
			embed.set_author(name=name, icon_url=reaction.message.author.avatar_url)
			embed.timestamp = datetime.datetime.now()
			found_embeds = reaction.message.attachments
			# if the message has an image attachment, post that
			if len(found_embeds) != 0:
				for item in found_embeds:
					post_image = item["url"]
					try:
						embed.set_image(url=post_image)
						info = config["starboard"]["emoji"] + ' ' + str(starcount) + ' ' + reaction.message.channel.mention + ' ID: ' + reaction.message.id
						await bot.send_message(starchan, info, embed=embed)
						await asyncio.sleep(1) # ratelimit shit idk
						break
					except:
						print("somehow couldn't set post image for starboard message")
			# otherwise look for image links
			else:
				image_links = re.findall(r"(http(s|):\/\/(.+?)(png|jpg|jpeg|gif|bmp))", reaction.message.content, flags=re.I|re.M)
				for item in image_links:
					# go through any image links that were found, try to embed them, and post the result
					try:
						embed.set_image(url=item[0])
						info = config["starboard"]["emoji"] + ' ' + str(starcount) + ' ' + reaction.message.channel.mention + ' ID: ' + reaction.message.id
						await bot.send_message(starchan, info, embed=embed)
						await asyncio.sleep(1)
						break
					except:
						pass
				# if none of the image links could be embedded, just post the message content without any image embed
				# no you're not reading this wrong, for loops DO have else clauses
				# this only runs if the for loop above never runs "break"
				else:
					info = config["starboard"]["emoji"] + ' ' + str(starcount) + ' ' + reaction.message.channel.mention + ' ID: ' + reaction.message.id
					await bot.send_message(starchan, info, embed=embed)
					await asyncio.sleep(1)

def setup(bot):
	bot.add_cog(Starboard(bot))