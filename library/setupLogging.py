import os
import logging


def getLogger(moduleName, DEBUG_LEVEL):

	# loggerName = os.path.basename(os.path.splitext(moduleName)[0])
	# logger = logging.getLogger(loggerName)
	logger = logging.getLogger(moduleName)
	streamHandler = logging.StreamHandler()
	streamHandler.setLevel(DEBUG_LEVEL)

	stdoutFormat = "%(name)s:%(levelname)s - %(message)s"
	stdoutFormatter = logging.Formatter(stdoutFormat)
	streamHandler.setFormatter(stdoutFormatter)
	logger.addHandler(streamHandler)
	logger.setLevel(DEBUG_LEVEL)
	# self.logger.addHandler(logging.StreamHandler())
	# logging.getLogger().setLevel(DEBUG_LEVEL)
	return logger
