import pickle

token = input("Insert bot token to continue: ")
try:
	tokenobject = open('tokenid.pkl', 'x+b')
except FileExistsError:
	tokenobject = open('tokenid.pkl', 'wb')
pickle.dump(token, tokenobject)
tokenobject.close()

config = open('config.cfg', 'w', encoding='utf-8')
default_config = \
"""
{
    "automod": {
        "autoban_mins": 30,
        "banlog_channel": "305194878139367427"
    },
    "broadcasting": {
        "announce_channel": "301798483525107712",
        "broadcast_vc": "329322925641433088"
    },
    "main": {
        "listening_channels": [
            "299408971381473281",
            "361691598939226123"
        ],
        "log_backup_count": 1,
        "log_filepath": "chairbot9000.log",
        "max_log_size_bytes": 10000000,
        "mod_role": "HYPERTHINK",
        "prefix": "&"
    },
    "reporting": {
        "report_channel": "326122367795593226"
    },
    "starboard": {
        "emoji": "⭐",
        "mod_override": "true",
        "star_amount": 7,
        "star_channel": "326254078403543041"
    }
}
"""
config.write(default_config)
config.close()

try:
	open('chairbot9000.log', 'x').close()
except FileExistsError:
	pass
print("Setup complete; run main.py now!")