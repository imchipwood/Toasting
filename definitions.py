import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(ROOT_DIR, u'config')
DATA_DIR = os.path.join(ROOT_DIR, u'data')

BASE_CONFIG_FILE_NAME = 'baseConfig.json'


def GetBaseConfigurationFilePath():
	"""
	Get the absolute path to the base configuration file
	@return: path to config file
	@rtype: str
	"""
	return os.path.join(CONFIG_DIR, BASE_CONFIG_FILE_NAME)


def GetDataFilePath(filename):
	"""
	Get the path to a data file (doesn't have to exist)
	@param filename: target filename
	@type filename: str
	@return: full path to file in data dir
	@rtype: str
	"""
	return os.path.join(DATA_DIR, filename)
