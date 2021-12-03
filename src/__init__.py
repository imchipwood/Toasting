import os

IS_RASPBERRY_PI = os.uname().machine == "armv7l"
IS_TEAMCITY = os.environ.get("IS_TEAMCITY") == "TRUE"
