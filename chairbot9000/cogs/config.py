import json
import os

class UpdateConfig:
	@staticmethod
	def save_config(config):
		config_path = os.path.abspath(os.path.dirname(__file__))
		config_path = os.path.join(config_path, "../misc/config.cfg")
		file = open(config_path, 'w', encoding='utf-8')
		file.write(json.dumps(config, indent=4, sort_keys=True, ensure_ascii=False))
		file.close()
	# don't use this, use the global var
	@staticmethod
	def read_config():
		config_path = os.path.abspath(os.path.dirname(__file__))
		config_path = os.path.join(config_path, "../misc/config.cfg")
		config = open(config_path, 'r', encoding='utf-8')
		out = json.load(config)
		config.close()
		return out

def init():
	global cfg
	# use this whenever you need the config
	cfg = UpdateConfig.read_config()