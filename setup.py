import pickle

token = input("Insert bot token to continue: ")
try:
	tokenobject = open('tokenid.pkl', 'x+b')
except FileExistsError:
	tokenobject = open('tokenid.pkl', 'wb')
pickle.dump(token, tokenobject)
tokenobject.close()

try:
	config = open('config.cfg', 'x+', encoding='utf-8')
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
        "mod_override": "false",
        "star_amounts": {
            "global": 5,
            "insert_channel_name_here": 13
        },
        "star_channel": "326254078403543041"
    },
    "memes": {
        "iloveyou": "OK I ADMIT IT I LOVE YOU OK i fucking love you and it breaks my heart when i see you play with someone else or anyone commenting in your profile i just want to be your boyfriend and put a heart in my profile linking to your profile and have a walltext of you commenting cute things i want to play video games talk in discord all night and watch a movie together but you just seem so uninterested in me it fucking kills me and i cant take it anymore i want to remove you but i care too much about you so please i'm begging you to either love me back or remove me and NEVER contact me again it hurts so much to say this because i need you by my side but if you don't love me then i want you to leave because seeing your icon in my friendlist would kill me everyday of my pathetic life",
        "bruce": "Hey its bruce from the lab. I just wanted to say that you're honestly the most beautiful girl I've ever seen. I don't mean to be creepy or anything i just couldn't help myself from approaching u once i saw u talking to mike",
        "bruce2": "Hey its lab from the bruce. I just wanted to say that you're honestly the most ugly girl I've ever seen. I don't mean to be amazing or anything i just couldn't help myself from approaching u once i saw u talking to mike",
        "hands": "Thanks bud, so kind\nYour hands were warm\nAnd very very tiny",
        "lovely": "My dearest long legged, lovely, picturesque treasure, how are you doing today? I'm better now that you're here -- while you're still responding, do you want to grab a drink later? Get something to eat? Get married? The usual",
        "confess": "Your such a fucking bitch honestly you told me to confess and now your turning me down why does anyone like you I hope you take your ugly face and [redacted]",
        "saki": "l    i    t    e    r    a    l    l    y    a    l    l    d    a    y    e    v    e    r    y    d    a    y    <    3"
    }
}
"""
	config.write(default_config)
	config.close()
except FileExistsError:
	pass

print("Setup complete; run main.py now!")
