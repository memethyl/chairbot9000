import asyncio
from   .           import config
import datetime
from   discord.ext import commands
import discord
import json
from   .misc       import sendembed
import os
import re
from   typing      import Union

class Starboard(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	@commands.group()
	async def starboard(self, ctx):
		"""&starboard <set/num/addpost> [...]"""
		if ctx.invoked_subcommand is None:
			content = "Correct syntax: `&starboard <set/num/addpost> [...]`"
			await sendembed(channel=ctx.channel, color=discord.Colour.dark_red(),
							title="Invalid command syntax", content=content)
	@starboard.command(description="Set the channel that starboard messages should be posted in.")
	async def set(self, ctx, channel: str):
		channel = ctx.guild.get_channel(int(re.findall(r"<#(\d+)>", channel)[0]))
		if channel:
			config.cfg["starboard"]["star_channel"] = channel.id
			config.UpdateConfig.save_config(config.cfg)
			content = f"Starboard channel set to {channel.mention}."
			await sendembed(channel=ctx.channel, color=discord.Colour.dark_green(),
							title="Starboard Channel Set", content=content)
		else:
			content = "Correct syntax: `&starboard set <channel mention>`"
			await sendembed(channel=ctx.channel, color=discord.Colour.dark_red(),
							title="Invalid command syntax", content=content)
	@starboard.command(description="Set the number of stars required for a post to go on the board. (0 to remove)")
	async def num(self, ctx, channel: str, amount: int):
		channel = ctx.guild.get_channel(int(re.findall(r"<#(\d+)>", channel)[0]))
		if amount == 0:
			try:
				del config.cfg["starboard"]["star_amounts"][channel.name]
				config.UpdateConfig.save_config(config.cfg)
				content = f"Removed amount of stars for {channel.mention}; channel now defaults to {config.cfg['starboard']['star_amounts']['global']}."
				await sendembed(channel=ctx.channel, color=discord.Colour.dark_green(),
								title="Removed Star Amount", content=content)
			except KeyError:
				content = f"Error: {channel.mention} doesn't have a custom star amount!"
				await sendembed(channel=ctx.channel, color=discord.Colour.dark_red(),
								title="Invalid command", content=content)
		else:
			config.cfg["starboard"]["star_amounts"][channel.name] = amount
			config.UpdateConfig.save_config(config.cfg)
			content = f"Required amount of stars for {channel.mention} set to {str(amount)}."
			await sendembed(channel=ctx.channel, color=discord.Colour.dark_green(),
							title="Star Amount Set", content=content)
	@starboard.command(description="Blacklist a user from the starboard, preventing any of their posts from making it there.")
	async def blacklist(self, ctx, user: Union[int, discord.User]): # user can be an ID or a mention
		if type(user) is int:
			config.cfg["starboard"]["blacklisted_users"].append(user)
		else:
			config.cfg["starboard"]["blacklisted_users"].append(user.id)
		config.UpdateConfig.save_config(config.cfg)
		content = "User has been blacklisted from the starboard. Their posts will no longer be posted there."
		await sendembed(channel=ctx.channel, color=discord.Colour.dark_green(),
						title="User Blacklisted", content=content)
	@starboard.command(description="Manually add a post to the starboard. Useful for when chairbot decides to ignore a post")
	async def addpost(self, ctx, message_chan: str, message_id: int):
		# extract ID from channel mention before grabbing the message itself
		message_chan = ctx.guild.get_channel(int(re.findall(r"<#(\d+)>", message_chan)[0]))
		try:
			message = await message_chan.get_message(message_id)
		except discord.errors.NotFound:
			await ctx.channel.send(f"Message ID {message_id} was not found in {message_chan.mention}!")
			return
		# get star count on the post
		reacts = message.reactions
		starlist = starcount = None
		for react in reacts:
			if react.emoji == config.cfg["starboard"]["emoji"]:
				starlist = [x async for x in react.users()]
				starcount = len(starlist)
				break
		else:
			return
		await Starboard.post_to_starboard(self.bot, message, starcount)
	# this is the function that actually posts stuff to the starboard
	@staticmethod
	async def post_to_starboard(bot, message, starcount):
		# start the actual embed now
		embed = discord.Embed(color=discord.Colour.gold(), description="[Jump To]("+message.jump_url+")\n\n"+message.content)
		embed.set_author(name=message.author.name+"#"+message.author.discriminator,
						 icon_url=message.author.avatar_url)
		starchan = bot.get_channel(config.cfg["starboard"]["star_channel"])
		embed.timestamp = datetime.datetime.now()
		found_embeds = message.attachments
		# if the message has an image attachment, use that
		if len(found_embeds) != 0:
			for item in found_embeds:
				try:
					post_image = item.url
					embed.set_image(url=post_image)
					break
				except:
					pass
		# otherwise look for image links
		else:
			image_links = re.findall(r"(http(s|):\/\/(.+?)(png|jpg|jpeg|gif|bmp))", message.content, flags=re.I|re.M)
			for item in image_links:
				# go through any image links that were found, and try to embed them
				try:
					embed.set_image(url=item[0])
					break
				except:
					pass
		content = config.cfg["starboard"]["emoji"] + " " + str(starcount) + " " + message.channel.mention + " " + "ID: " + str(message.id)
		async for history_message in starchan.history(limit=config.cfg["starboard"]["repost_history"]):
			# if the post already exists on the board, edit that post with the updated star count instead of making a new post
			if str(message.id) in history_message.content:
				starred_message = await starchan.get_message(history_message.id)
				await starred_message.edit(content=content, embed=embed)
				break
		else:
			starred_message = await starchan.send(content=content, embed=embed)
	@commands.command(description="Set whether or not moderators can override the star requirement.\n(to set the mod role, see &modset)")
	async def modstar(self, ctx, value: str):
		"""&modstar <true/false>"""
		if value.lower() == 'true' or value.lower() == 'false':
			config.cfg["starboard"]["role_override"] = value.lower()
			config.UpdateConfig.save_config(config.cfg)
			content = f"Mod star override set to {value.lower()}."
			color = discord.Colour.dark_green() if value.lower() == 'true' else discord.Colour.dark_red()
			await sendembed(channel=ctx.channel, color=color,
							title="Mod Star Override Set", content=content)
		else:
			content = "Correct syntax: `&modstar <true/false>`"
			await sendembed(channel=ctx.channel, color=discord.Colour.dark_red(),
							title="Invalid command syntax", content=content)
	@staticmethod
	def modcheck(bot, config, user):
		server = bot.get_guild(214249708711837696)
		member = server.get_member(user.id)
		# get_member occasionally returns None when it shouldn't,
		# so just don't bother if it starts misbehaving
		if not member: return False
		for role in member.roles:
			if role.id == config["starboard"]["override_role"]:
				return True
		return False
	@staticmethod
	async def post_starred(bot, config, message, reaction_emoji, user):
		"""Checks a message's star count. If the star count meets or exceeds the amount required, put the message on the board."""
		reacts = message.reactions
		mod_starred = False
		starlist = None
		starcount = None
		starcount_reached = False
		# if the post is older than a week, don't bother putting it on the board
		if (datetime.datetime.now() - message.created_at).total_seconds() > 604800:
			return
		# check if the poster of the starred message is blacklisted from the starboard
		if message.author.id in config["starboard"]["blacklisted_users"]:
			return
		# count the number of stars a post has
		for react in reacts:
			if react.emoji == config["starboard"]["emoji"]:
				starlist = [x async for x in react.users()]
				starcount = len(starlist)
				break
		else:
			return
		# check if the star count was reached
		try:
			# if there's a star requirement for a specific channel, and the starred message is in that channel,
			# check if the star count surpasses the requirement for that channel
			if starcount >= config["starboard"]["star_amounts"][message.channel.name]:
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
		if message.author.id == user.id:
			await message.remove_reaction(reaction_emoji, message.author)
			# count the number of self-star alerts out of the last 50 messages
			counter = 0
			async for message in message.channel.history(limit=50):
				if "IS A THOT AND SELF-STARRED THEIR MEME" in message.content:
					counter += 1
			# if there's been less than three, send a self-star alert
			# this is to prevent spam from CERTAIN THOTS THAT LOVE SPAMMING IT
			if counter < 3:
				selfstar_alert = '🚨 🚨 ' + user.mention + ' IS A THOT AND SELF-STARRED THEIR MEME 🚨 🚨'
				await message.channel.send(selfstar_alert)
			return
		if starcount_reached and message.author.id != bot.user.id:
			await Starboard.post_to_starboard(bot, message, starcount)

def setup(bot):
	bot.add_cog(Starboard(bot))