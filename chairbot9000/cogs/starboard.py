import asyncio
from . import config
import datetime
from discord.ext import commands
import discord
import json
from .misc import sendembed
import re

class Starboard():
	def __init__(self, bot):
		self.bot = bot
	@commands.group(pass_context=True)
	async def starboard(self, ctx):
		"""&starboard [set/num/addpost] ..."""
		if ctx.invoked_subcommand is None:
			content = "Correct syntax: `&starboard [set/num] [channel/minimum stars]"
			await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_red(),
							title="Invalid command syntax", content=content)
	@starboard.command(pass_context=True, description="Set the channel that starboard messages should be posted in.")
	async def set(self, ctx, channel: discord.Channel):
		if channel:
			config.cfg["starboard"]["star_channel"] = channel.id
			config.UpdateConfig.save_config(config.cfg)
			content = "Starboard channel set to {0}.".format(channel.mention)
			await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_green(),
							title="Starboard Channel Set")
		else:
			content = "Correct syntax: `&starboard set [channel]"
			await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_red(),
							title="Invalid command syntax", content=content)
	@starboard.command(pass_context=True, description="Set the number of stars required for a post to go on the board. (0 to remove)")
	async def num(self, ctx, channel: discord.Channel, amount: int):
		if amount == 0:
			try:
				del config.cfg["starboard"]["star_amounts"][channel.name]
				config.UpdateConfig.save_config(config.cfg)
				content = "Removed amount of stars for {0}; channel now defaults to {1}.".format(channel.mention, config.cfg["starboard"]["star_amounts"]["global"])
				await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_green(),
								title="Removed Star Amount", content=content)
			except KeyError:
				content = "Error: {0} doesn't have a custom star amount!".format(channel.mention)
				await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_red(),
								title="Invalid command", content=content)
		else:
			config.cfg["starboard"]["star_amounts"][channel.name] = amount
			config.UpdateConfig.save_config(config.cfg)
			content = "Required amount of stars for {0} set to {1}.".format(channel.mention, str(amount))
			await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_green(),
							title="Star Amount Set", content=content)
	@starboard.command(pass_context=True, description="Manually add a post to the starboard. Useful for when chairbot decides to ignore a post")
	async def addpost(self, ctx, message_chan: discord.Channel, message_id: str):
		message = await self.bot.get_message(message_chan, message_id)
		# get star count on the post
		reacts = message.reactions
		starlist = starcount = None
		for react in reacts:
			if react.emoji == config.cfg["starboard"]["emoji"]:
				starlist = await self.bot.get_reaction_users(react)
				starcount = len(starlist)
				break
		else:
			return
		# copy-paste powers, activate
		embed = discord.Embed(color=discord.Colour.gold(), description=message.content)
		name = message.author.name + "#" + message.author.discriminator
		starchan = self.bot.get_channel(config.cfg["starboard"]["star_channel"])
		embed.set_author(name=name, icon_url=message.author.avatar_url)
		embed.timestamp = datetime.datetime.now()
		found_embeds = message.attachments
		# if the message has an image attachment, post that
		if len(found_embeds) != 0:
			for item in found_embeds:
				try:
					post_image = item["url"]
					embed.set_image(url=post_image)
					info = config.cfg["starboard"]["emoji"] + ' ' + str(starcount) + ' ' + message.channel.mention + ' ID: ' + message.id
					await self.bot.send_message(starchan, info, embed=embed)
					await asyncio.sleep(1) # ratelimit shit idk
					break
				except:
					pass
		# otherwise look for image links
		else:
			image_links = re.findall(r"(http(s|):\/\/(.+?)(png|jpg|jpeg|gif|bmp))", message.content, flags=re.I|re.M)
			for item in image_links:
				# go through any image links that were found, try to embed them, and post the result
				try:
					embed.set_image(url=item[0])
					info = config.cfg["starboard"]["emoji"] + ' ' + str(starcount) + ' ' + message.channel.mention + ' ID: ' + message.id
					await self.bot.send_message(starchan, info, embed=embed)
					await asyncio.sleep(1)
					break
				except:
					pass
			# if none of the image links could be embedded, just post the message content without any image embed
			# no you're not reading this wrong, for loops DO have else clauses
			# this only runs if the for loop above never runs "break"
			else:
				info = config.cfg["starboard"]["emoji"] + ' ' + str(starcount) + ' ' + message.channel.mention + ' ID: ' + message.id
				await self.bot.send_message(starchan, info, embed=embed)
				await asyncio.sleep(1)
	@commands.command(pass_context=True, description="Set whether or not moderators can override the star requirement.\n(to set the mod role, see &modset)")
	async def modstar(self, ctx, value: str):
		if value.lower() == 'true' or value.lower() == 'false':
			config.cfg["starboard"]["role_override"] = value.lower()
			config.UpdateConfig.save_config(config.cfg)
			content = "Mod star override set to {0}.".format(value.lower())
			color = discord.Colour.dark_green() if value.lower() == 'true' else discord.Colour.dark_red()
			await sendembed(self.bot, channel=ctx.message.channel, color=color,
							title="Mod Star Override Set", content=content)
		else:
			content = "Correct syntax: `&modstar [true/false]`"
			await sendembed(self.bot, channel=ctx.message.channel, color=discord.Colour.dark_red(),
							title="Invalid command syntax", content=content)
	@staticmethod
	def modcheck(bot, config, user):
			server = bot.get_server('214249708711837696')
			member = server.get_member(user.id)
			for role in member.roles:
				if role.name == config["starboard"]["override_role"]:
					return True
			return False
	@staticmethod
	async def post_starred(bot, config, reaction, user):
		"""Checks a message's star count. If the star count meets or exceeds the amount required, put the message on the board."""
		reacts = reaction.message.reactions
		mod_starred = False
		starlist = None
		starcount = None
		starcount_reached = False

		# count the number of stars a post has
		for react in reacts:
			if react.emoji == config["starboard"]["emoji"]:
				starlist = await bot.get_reaction_users(react)
				starcount = len(starlist)
				break
		else:
			return

		# check if the star count was reached
		try:
			# if there's a star requirement for a specific channel, and the starred message is in that channel,
			# check if the star count surpasses the requirement for that channel
			if starcount >= config["starboard"]["star_amounts"][reaction.message.channel.name]:
				starcount_reached = True
		# if there isn't a channel-specific star count this message must follow,
		except KeyError:
			# just check to see if it meets the global requirement
			if starcount >= config["starboard"]["star_amounts"]["global"]:
				starcount_reached = True
		# check if a mod starred the post
		for reactor in starlist:
			if Starboard.modcheck(bot, config, reactor) and config["starboard"]["role_override"] == "true":
				starcount_reached = True
				break

		# anti-self-star code
		if reaction.message.author in starlist:
			await bot.remove_reaction(reaction.message, reaction.emoji, reaction.message.author)
			# count the number of self-star alerts out of the last 50 messages
			counter = 0
			async for message in bot.logs_from(reaction.message.channel, limit=50):
				if "IS A THOT AND SELF-STARRED THEIR MEME" in message.content:
					counter += 1
			# if there's been less than three, send a self-star alert
			# this is to prevent spam from CERTAIN THOTS THAT LOVE SPAMMING IT
			if counter < 3:
				selfstar_alert = '🚨 🚨 ' + reaction.message.author.mention + ' IS A THOT AND SELF-STARRED THEIR MEME 🚨 🚨'
				await bot.send_message(reaction.message.channel, selfstar_alert)
			return

		# the code that actually posts stuff to the starboard
		if starcount_reached and reaction.message.author.id != bot.user.id:
			# start posting
			starchan = bot.get_channel(config["starboard"]["star_channel"])
			async for found_message in bot.logs_from(starchan, limit=50):
				# if the ID of the starred message was in any of the last 50 starboard posts,
				if reaction.message.id in found_message.content and found_message.author.id == bot.user.id:
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