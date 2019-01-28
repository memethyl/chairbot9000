#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import pickle

# set up bot token
token = input("Insert bot token to continue: ")
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

def config_setup(config):
	default_config = {
		"automod": {
		},
		"broadcasting": {
		},
		"main": {
			"perms": {
			},
			"prefix": "&"
		},
		"memes": {
		},
		"reporting": {
		},
		"starboard": {
			"emoji": "⭐",
			"repost_history": 100,
			"star_amounts": {
			}
		}
	}
	default_config["automod"]["autoban_mins"] = int(input("How young should an account be (less than X minutes old) for chairbot9000 to autoban it? "))
	default_config["automod"]["banlog_channel"] = int(input("Provide the ID (e.g. 123456789012345678) of the text channel you want chairbot to log autobans to. "))
	
	default_config["broadcasting"]["announce_channel"] = int(input("Provide the ID of the text channel you want chairbot to announce broadcasts in. "))
	default_config["broadcasting"]["broadcast_vc"] = int(input("Provide the ID of the voice channel you want to do broadcasts in. "))

	with input("The default chairbot prefix is '&'.\nIf you want to use a certain prefix for chairbot commands (e.g. !help instead of &help), enter it now. ") as prefix:
		if prefix:
			default_config["main"]["prefix"] = prefix
	default_config["main"]["perms"]["global"] = input("Provide the NAME of the minimum role required to use ANY chairbot command. ")
	print("Note: If you want to require higher roles for certain commands, run `{}help perms set` once the bot is online.".format(default_config["main"]["prefix"]))

	default_config["reporting"]["report_channel"] = int(input("NOTE: IN ORDER FOR REPORTING TO WORK, THE \"YAGPDB\" BOT (https://yagpdb.xyz/) MUST BE USED; THIS MAY CHANGE IN A LATER UPDATE\nProvide the ID of the text channel you want YAGPDB reports to be sent to and handled in. "))
	
	with input("Provide the emoji that people should react with to put messages on the starboard. If no input is provided, this will default to ⭐. ") as emoji:
		if emoji:
			default_config["starboard"]["emoji"] = emoji
	with input("Do you want people with a certain role to be able to put messages on the starboard, regardless of reaction count? (y/n) ") as role_override:
		if role_override.lower() is 'y':
			default_config["starboard"]["override_role"] = input("In that case, enter the NAME of the role required to do this. ")
		elif role_override.lower() is 'n':
			print("Okay, but note that you'll have to set this later if you change your mind.")
		else:
			print("Invalid input provided; defaulting to 'n'.")
			default_config["starboard"]["role_override"] = 'n'
	with input("How many previously added posts do you want chairbot to look through when checking if a post already exists on the starboard? (default is 100) ") as repost_history:
		if repost_history:
			default_config["starboard"]["repost_history"] = int(repost_history)
	default_config["starboard"]["star_amounts"]["global"] = int(input("Please enter the default number of reactions required to put a message on the starboard. "))
	print("If you want certain channels to require more reactions than others, run `{}help starboard num` once the bot is online.".format(default_config["main"]["prefix"]))
	default_config["starboard"]["star_channel"] = int(input("Please enter the ID of the channel you want to use as the starboard. "))
	
	config.write(default_config)
	config.close()

try:
	config = open('chairbot9000/misc/config.cfg', 'x+', encoding='utf-8')
	config_setup(config)
except FileExistsError:
	config_setup(config) if input("It seems that config.cfg already exists; do you wish to reconfigure it? (y/n) ").lower() is 'y' else None

print("Setup complete; make sure config.cfg is set up properly, then run main.py!")
