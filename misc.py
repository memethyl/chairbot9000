import datetime
import discord

# if you have a circular dependency, put the offending function in this file and change your imports

async def sendembed(client, channel, color, title, content, author=None):
	embed = discord.Embed(colour=color, type='rich', title=title, description=content)
	embed.timestamp = datetime.datetime.now()
	if author == None:
		await client.send_message(channel, embed=embed)
	else:
		embed.set_author(name=author.name, icon_url=author.avatar_url)
		await client.send_message(channel, embed=embed)