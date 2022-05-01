import os
import logging

MODEL_NAME = "Toasting"

CONFIG_KEY_TARGET = "target"
CONFIG_KEY_DURATION = "duration"
DEBUG_LEVEL = logging.INFO

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(ROOT_DIR, u'config')
DATA_DIR = os.path.join(ROOT_DIR, u'data')

BASE_CONFIG_FILE_NAME = 'baseConfig.json'


def get_configuration_file_path(file_name):
	"""
	Get the absolute path to a file in the configuration directory
	@param file_name: name of file in config dir
	@type file_name: str
	@return: path to config file
	@rtype: str
	"""
	return os.path.join(CONFIG_DIR, file_name)


def get_base_configuration_file_path():
	"""
	Get the absolute path to the base configuration file
	@return: path to config file
	@rtype: str
	"""
	return get_configuration_file_path(BASE_CONFIG_FILE_NAME)


def get_data_file_path(file_name):
	"""
	Get the path to a data file (doesn't have to exist)
	@param file_name: target filename
	@type file_name: str
	@return: full path to file in data dir
	@rtype: str
	"""
	return os.path.join(DATA_DIR, file_name)
