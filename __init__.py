#!/usr/bin/python
# 
# This initializes the bot on startup, sets some environment variables
# that are used in the bot, and gets it going.
#
# Need to load the scores, if they exist, and connect to irc, displaying
# a welcome message.
#
# Scores should be kept in a class which will hold a nick -> score dict
# object, and at the end of every question will dump the dict to json
# where it can be loaded from. This might get weird if people start using
# weird nicks, but we'll cross that road when we get to it.
#
# irc connection should be a class, and we should use twisted. We don't
# really care if people come and go, since everyone in the channel is
# playing. Should handle this like karma. Watch all traffic, and if
# someone blurts out a string that matches the answer, they get the points.
# If they haven't scored before, add them to the scoreboard and give them
# their points, else, add their points to their total. Then dump the json.
#
# This bot requires there to be a ../questions/ directory with text files
# in it. These files are named after there genres, so "80s Films.txt"
# and the like. While the bot is running, it will randomly choose a
# file from this directory, open it, randomly choose a line, which is
# a question*answer pair, then load that into a structure to be asked.
#
# Once the question is loaded, the bot will ask the IRC channel the
# question, wait a period of time, show a character, then ask the question
# again.
#
# The bot should respond to /msgs, so that users can check their scores,
# and admins can give admin commands, like die, show all scores, edit
# player scores, etc. Commands should be easy to implement.
#
# Every so often between questions the bot should list the top ranked
# players, wait some, then continue.


