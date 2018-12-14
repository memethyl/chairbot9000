#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import pickle

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

try:
	config = open('chairbot9000/misc/config.cfg', 'x+', encoding='utf-8')
	default_config = \
"""
{
    "automod": {
        "autoban_mins": 30,
        "banlog_channel": 305194878139367427,
        "invite_regex": "((discord\\.gg|discordapp\\.com)\\/(invite\\/|).*)|(.*?(etivni\\/|)\\/(gg\\.drocsid|moc\\.ppadrocsid))"
    },
    "broadcasting": {
        "announce_channel": 301798483525107712,
        "broadcast_vc": 329322925641433088
    },
    "main": {
        "perms": {
            "global": "HYPERTHINK"
        },
        "prefix": "&"
    },
    "memes": {
    },
    "reporting": {
        "report_channel": 326122367795593226
    },
    "starboard": {
        "emoji": "⭐",
        "role_override": "false",
		"override_role": "HYPERTHINK",
        "star_amounts": {
            "global": 5
        },
        "star_channel": 326254078403543041
    }
}
"""
	config.write(default_config)
	config.close()
except FileExistsError:
	pass

print("Setup complete; make sure config.cfg is set up properly, then run main.py!")
