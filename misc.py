import datetime
import discord
import json

# if you have a circular dependency, put the offending function in this file and change your imports

async def sendembed(client, channel, color, title, content, author=None):
	embed = discord.Embed(colour=color, type='rich', title=title, description=content)
	embed.timestamp = datetime.datetime.now()
	if author == None:
		await client.send_message(channel, embed=embed)
	else:
		embed.set_author(name=author.name, icon_url=author.avatar_url)
		await client.send_message(channel, embed=embed)

class Config:
	# assign your config variable to save_config whenever you have to modify it at all
	@staticmethod
	def save_config(config):
		file = open('config.cfg', 'w', encoding='utf-8')
		file.write(json.dumps(config, indent=4, sort_keys=True, ensure_ascii=False))
		file.close()
		return Config.read_config()
	@staticmethod
	def read_config():
		config = open('config.cfg', 'r', encoding='utf-8')
		out = json.load(config)
		config.close()
		return out