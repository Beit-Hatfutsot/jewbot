import logging
import os

try:
    import local_config
except ImportError:
    local_config = object()

BASE_DIR = os.path.dirname(__file__)
bot_path = lambda *dirs: os.path.join(BASE_DIR, *dirs)

BOT_DATA_DIR = getattr(local_config, "JEWBOT_DATA_DIR", "")
BOT_DATA_DIR = BOT_DATA_DIR if BOT_DATA_DIR else bot_path("data")
BOT_EXTRA_PLUGIN_DIR = bot_path("plugins")

BOT_LOG_FILE = bot_path("errbot.log")
BOT_LOG_LEVEL = {"DEBUG": logging.DEBUG,
                 "INFO": logging.INFO,
                 "WARNING": logging.WARNING,
                 "ERROR": logging.ERROR,
                 "CRITICAL": logging.CRITICAL}[getattr(local_config, "JEWBOT_LOG_LEVEL", "DEBUG")]

BACKEND = getattr(local_config, "JEWBOT_BACKEND", "Text")  # By default errbot will start in text mode (console only mode) and will answer commands from there.

if BACKEND == "Slack":
    BOT_IDENTITY = {
        'token': local_config.JEWBOT_SLACK_TOKEN,
    }
    BOT_ADMINS = ["@{}".format(admin.strip().strip("@")) for admin in local_config.JEWBOT_SLACK_ADMINS.split(",")]
    BOT_ALT_PREFIXES = ('@jewbot',)
    CHATROOM_PRESENCE = ()
else:
    BOT_ADMINS = ('CHANGE ME',)  # !! Don't leave that to "CHANGE ME" if you connect your errbot to a chat system !!

DBS_BACK_DIR = getattr(local_config, "JEWBOT_DBS_BACK_DIR", bot_path("..", "dbs-back"))
DBS_BACK_ENV = getattr(local_config, "JEWBOT_DBS_BACK_ENV", bot_path("..", "dbs-back", "env"))
