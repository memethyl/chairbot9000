import json

class UpdateConfig:
	@staticmethod
	def save_config(config):
		file = open('config.cfg', 'w', encoding='utf-8')
		file.write(json.dumps(config, indent=4, sort_keys=True, ensure_ascii=False))
		file.close()
	# don't use this, use the global var
	@staticmethod
	def read_config():
		config = open('config.cfg', 'r', encoding='utf-8')
		out = json.load(config)
		config.close()
		return out

def init():
	global cfg
	# use this whenever you need the config
	cfg = UpdateConfig.read_config()