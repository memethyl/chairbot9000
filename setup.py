#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import pickle
import sqlite3

# set up bot token
token = input("\nInsert bot token to continue: ")
try:
	tokendir = 'chairbot9000/misc/tokenid.pkl'
	os.makedirs(os.path.dirname(tokendir), exist_ok=True)
	tokenobject = open(tokendir, 'x+b')
except FileExistsError:
	tokendir = 'chairbot9000/misc/tokenid.pkl'
	os.makedirs(os.path.dirname(tokendir), exist_ok=True)
	tokenobject = open(tokendir, 'wb')
pickle.dump(token, tokenobject)
tokenobject.close()

memedir = 'chairbot9000/misc/memed_users.db'
os.makedirs(os.path.dirname(memedir), exist_ok=True)
conn = sqlite3.connect(memedir)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS memed_users 
			 (user_id integer, expiration timestamp)''')
conn.commit()
conn.close()

def config_setup(config):
	default_config = {
		"moderation": {
			"invite_regex": "discordapp\\.com\\/invite\\/|discord\\.gg\\/|\\/gg\\.drocsid|\\/etivni\\/moc.ppadrocsid",
			"meme_channel": 0
		},
		"broadcasting": {
		},
		"main": {
			"perms": {
			},
			"prefix": "&",
			"vc_text_channel": 0 # todo: add this to setup script
		},
		"reporting": {
		},
		"starboard": {
			"blacklisted_users": [

			],
			"emoji": "⭐",
			"override_role": 0,
			"repost_history": 100,
			"star_amounts": {
			}
		}
	}
	default_config["moderation"]["autoban_mins"] = int(input("\nHow young should an account be (less than X minutes old) for chairbot9000 to autoban it? "))
	default_config["moderation"]["banlog_channel"] = int(input("\nProvide the ID (e.g. 123456789012345678) of the text channel you want chairbot to log autobans to. "))

	if meme_channel := input(f"\nPlease enter the ID of the channel you want to use as the meme channel. You CAN leave this blank, but {default_config['main']['prefix']}meme will not work."):
		default_config["moderation"]["meme_channel"] = int(meme_channel)
	
	default_config["broadcasting"]["announce_channel"] = int(input("\nProvide the ID of the text channel you want chairbot to announce broadcasts in. "))
	default_config["broadcasting"]["broadcast_vc"] = int(input("\nProvide the ID of the voice channel you want to do broadcasts in. "))

	if prefix:=input("\nThe default chairbot prefix is '&'.\nIf you want to use a certain prefix for chairbot commands (e.g. !help instead of &help), enter it now. "):
		default_config["main"]["prefix"] = prefix

	default_config["main"]["perms"]["global"] = int(input("\nProvide the ID of the minimum role required to use ANY chairbot command. "))
	print(f"Note: If you want to require higher roles for certain commands, run `{default_config['main']['prefix']}help perms set` once the bot is online.")

	default_config["reporting"]["report_channel"] = int(input("\nNOTE: IN ORDER FOR REPORTING TO WORK, THE \"YAGPDB\" BOT (https://yagpdb.xyz/) MUST BE USED; THIS MAY CHANGE IN A LATER UPDATE\nProvide the ID of the text channel you want YAGPDB reports to be sent to and handled in. "))

	if emoji := input("\nProvide the emoji that people should react with to put messages on the starboard. If no input is provided, this will default to ⭐. "):
		default_config["starboard"]["emoji"] = emoji

	if (role_override := input("\nDo you want people with a certain role to be able to put messages on the starboard, regardless of reaction count? (y/n) ").lower()) == 'y':
		default_config["starboard"]["role_override"] = 'true'
		default_config["starboard"]["override_role"] = int(input("\nIn that case, enter the ID of the role required to do this. "))
	elif role_override == 'n':
		print("Okay, but note that you'll have to set this later if you change your mind.")
		default_config["starboard"]["role_override"] = 'false'
	else:
		print("Invalid input provided; defaulting to 'n'.")
		default_config["starboard"]["role_override"] = 'false'

	if repost_history := input("\nHow many previously added posts do you want chairbot to look through when checking if a post already exists on the starboard? (default is 100) "):
		default_config["starboard"]["repost_history"] = int(repost_history)

	default_config["starboard"]["star_amounts"]["global"] = int(input("\nPlease enter the default number of reactions required to put a message on the starboard. "))
	print(f"If you want certain channels to require more reactions than others, run `{default_config['main']['prefix']}help starboard num` once the bot is online.")
	default_config["starboard"]["star_channel"] = int(input("\nPlease enter the ID of the channel you want to use as the starboard. "))
	
	config.write(str(default_config).replace('\'', '"'))
	config.close()

try:
	config = open('chairbot9000/misc/config.cfg', 'x+', encoding='utf-8')
	config_setup(config)
except FileExistsError:
	if input("\nIt seems that config.cfg already exists; do you wish to reconfigure it? (y/n) ").lower() == 'y':
		config = open('chairbot9000/misc/config.cfg', 'w', encoding='utf-8')
		config_setup(config)

print("Setup complete; make sure config.cfg is set up properly, then run main.py!")
