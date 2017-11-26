import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(ROOT_DIR, u'config')
DATA_DIR = os.path.join(ROOT_DIR, u'data')

BASE_CONFIG_FILE_NAME = 'baseConfig.json'


def getBaseConfigurationFilePath():
	"""Get the absolute path to the base configuration file

	@return: str
	"""
	return os.path.join(CONFIG_DIR, BASE_CONFIG_FILE_NAME)
