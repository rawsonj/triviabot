# Example config for triviabot
#
# This file is part of triviabot
# Web site: https://github.com/rawsonj/triviabot)
#
# Copy this file to 'config.py', then edit 'config.py' to
# set your preferences.

GAME_CHANNEL = '#triviachannel'

ADMINS = ['admin']
# or a comma separated list
# ADMINS = ['admin','admin2']

Q_DIR = './questions/'

SAVE_DIR = './savedata/'

IDENT_STRING = 'password'

# Time (in seconds) between clues, and the wait time between questions.
# If ?skip is used, the interval doesn't apply
WAIT_INTERVAL = 30

# Colorize the text so it contrasts with the channel text.
# This makes it easier to play the game when people are chatting.
#
# \003 is the color-code prefix, the next two numbers
# is the foreground code, the last two numbers is the backgroudn code.
COLOR_CODE = '\00308,01'

# How fast will the bot output messages to the channel
LINE_RATE = 0.4

DEFAULT_NICK = 'triviabot'

SERVER = 'irc.freenode.net'

# Some servers support SSL, and some do not. If you have trouble connecting
# to your IRC network, you may have to disable SSL or change the server port
SERVER_PORT = 6667
USE_SSL = "YES"
