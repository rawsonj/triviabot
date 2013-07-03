#!/usr/bin/python2
# Copyright (C) 2013 Joe Rawson
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
#

import json
from os import listdir, path, makedirs
from random import choice

from twisted.words.protocols import irc
from twisted.internet import reactor
from twisted.internet import ssl
from twisted.internet.protocol import ClientFactory
from twisted.internet.task import LoopingCall

from lib.answer import Answer

import config

class triviabot(irc.IRCClient):
    '''
    This is the irc bot portion of the trivia bot.

    It implements the whole program so is kinda big. The algorithm is
    implemented by a series of callbacks, initiated by an admin on the
    server.
    '''
    def __init__(self):
        self._answer = Answer()
        self._question = ''
        self._scores = {}
        self._clue_number = 0
        self._admins = list(config.ADMINS)
        self._game_channel = config.GAME_CHANNEL
        self._current_points = 5
        self._questions_dir = config.Q_DIR
        self._lc = LoopingCall(self._play_game)
        self._load_game()
        self._votes = 0
        self._voters = []

    def _get_nickname(self):
        return self.factory.nickname

    nickname = property(_get_nickname)

    def _get_lineRate(self):
        return self.factory.lineRate

    lineRate = property(_get_lineRate)

    def _cmsg(self, dest, msg):
        """
        Write a colorized message.
        """

        self.msg(dest, "%s%s" % (config.COLOR_CODE, msg))

    def _gmsg(self, msg):
        """
        Write a message to the channel playing the trivia game.
        """

        self._cmsg(self._game_channel, msg)

    def _play_game(self):
        '''
        Implements the main loop of the game.
        '''
        points = { 0 : 5,
                   1 : 3,
                   2 : 2,
                   3 : 1
                 }
        if self._clue_number == 0:
            self._votes = 0
            self._voters = []
            self._get_new_question()
            self._current_points = points[self._clue_number]
            # Blank line.
            self._gmsg("")
            self._gmsg("Next question:")
            self._gmsg(self._question)
            self._gmsg("Clue: %s" % self._answer.current_clue())
            self._clue_number += 1
        # we must be somewhere in between
        elif self._clue_number < 4:
            self._current_points = points[self._clue_number]
            self._gmsg("Question:")
            self._gmsg(self._question)
            self._gmsg('Clue: %s' % self._answer.give_clue())
            self._clue_number += 1
        # no one must have gotten it.
        else:
            self._gmsg('No one got it. The answer was: %s' %
                       self._answer.answer)
            self._clue_number = 0
            self._get_new_question()
            #self._lc.reset()

    def signedOn(self):
        '''
        Actions to perform on signon to the server.
        '''
        self.join(self._game_channel)
        self.msg('NickServ', 'identify %s' % config.IDENT_STRING)
        print("Signed on as %s." % (self.nickname,))
        if self.factory.running:
            self._start(None,None,None)
        else:
            self._gmsg('Welcome to %s!' % self._game_channel)
            self._gmsg("Have an admin start the game when you are ready.")
            self._gmsg("For how to use this bot, just say ?help or")
            self._gmsg("%s help." % self.nickname)

    def joined(self, channel):
        '''
        Callback runs when the bot joins a channel
        '''
        print("Joined %s." %(channel,))

    def privmsg(self, user, channel, msg):
        '''
        Parses out each message and initiates doing the right thing
        with it.
        '''
        user,temp = user.split('!')
        print(user+" : "+channel+" : "+msg)
        # need to strip off colors if present.
        try:
            while not msg[0].isalnum() and not msg[0] == '?':
                msg = msg[1:]
        except IndexError:
            return

        # parses each incoming line, and sees if it's a command for the bot.
        try:
            if (msg[0]=="?"):
                command = msg.replace('?','').split()[0]
                args = msg.replace('?','').split()[1:]
                self.select_command(command, args, user, channel)
                return
            elif (msg.split()[0].find(self.nickname)==0):
                command = msg.split()[1]
                args = msg.replace(self.nickname,'').split()[2:]
                self.select_command(command, args, user, channel)
                return
            # if not, try to match the message to the answer.
            else:
                if msg.lower().strip() == self._answer.answer.lower():
                    self._winner(user,channel)
                    self._save_game()
        except:
            return

    def _winner(self,user,channel):
        '''
        Congratulates the winner for guessing correctly and assigns
        points appropriately, then signals that it was guessed.
        '''
        if channel != self._game_channel:
            self.msg(channel, "I'm sorry, answers must be given in the game channel.")
            return
        self._gmsg("%s GOT IT!" % user.upper())
        try:
            self._scores[user] += self._current_points
        except:
            self._scores[user] = self._current_points
        if self._current_points == 1:
            self._gmsg("%s point has been added to your score!" %
                       str(self._current_points))
        else:
            self._gmsg("%s points has been added to your score!" %
                       str(self._current_points))
        self._clue_number = 0
        self._get_new_question()

    def ctcpQuery(self, user, channel, msg):
        '''
        Responds to ctcp requests.
        Currently just reports them.
        '''
        print("CTCP recieved: "+user+":"+channel+": "+msg[0][0]+" "+msg[0][1])

    def _help(self,args,user,channel):
        '''
        Tells people how to use the bot.
        Replies differently if you are an admin or a regular user.
        Only responds to the user since there could be a game in
        progress.
        '''
        try:
            self._admins.index(user)
        except:
            self._cmsg(user, "I'm nameless's trivia bot.")
            self._cmsg(user, "Commands: score, standings, giveclue, help, "
                       "next, source")
            return
        self._cmsg(user, "I'm nameless's trivia bot.")
        self._cmsg(user, "Commands: score, standings, giveclue, help, next, "
                   "skip, source")
        self._cmsg("Admin commands: die, set <user> <score>, start, stop, "
                   "save")

    def _show_source(self,args,user,channel):
        '''
        Tells people how to use the bot.
        Only responds to the user since there could be a game in
        progress.
        '''
        self._cmsg(user, 'My source can be found at: '
                   'https://github.com/rawsonj/triviabot')

    def select_command(self, command, args, user, channel):
        '''
        Callback that responds to commands given to the bot.

        Need to differentiate between priviledged users and regular
        users.
        '''
        # set up command dicts.
        unpriviledged_commands = { 'score': self._score,
                                   'help' : self._help,
                                   'source' : self._show_source,
                                   'standings' : self._standings,
                                   'giveclue' : self._give_clue,
                                   'next' : self._next_vote,
                                   'skip': self._next_question
                                 }
        priviledged_commands = { 'die' : self._die,
                                 'set' : self._set_user_score,
                                 'start': self._start,
                                 'stop': self._stop,
                                 'save': self._save_game,
                               }
        print command, args, user, channel
        try:
            self._admins.index(user)
            is_admin = True
        except:
            is_admin = False

        # the following takes care of sorting out functions and
        # priviledges.
        if not is_admin and priviledged_commands.has_key(command):
            self.msg(channel, "%s: You don't tell me what to do." % user)
            return
        elif is_admin and priviledged_commands.has_key(command):
            priviledged_commands[command](args, user, channel)
        elif unpriviledged_commands.has_key(command):
            unpriviledged_commands[command](args, user, channel)
        else:
            self.describe(channel, '%slooks at %s oddly.' %
                          (config.COLOR_CODE, user))

    def _next_vote(self, args, user, channel):
        '''Implements user voting for the next question.

        Need to keep track of who voted, and how many votes.

        '''
        if not self._lc.running:
            self._gmsg("We aren't playing right now.")
            return
        try:
            self._voters.index(user)
            self._gmsg("You already voted, %s, give someone else a chance to "
                       "hate this question" % user)
            return
        except:
            if self._votes < 2:
                self._votes += 1
                self._voters.append(user)
                print self._voters
                self._gmsg("%s, you have voted. %s more votes needed to "
                           "skip." % (user, str(3-self._votes)))
            else:
                self._votes = 0
                self._voters = []
                self._next_question(None,None,None)

    def _start(self, args, user, channel):
        '''
        Starts the trivia game.

        TODO: Load scores from last game, if any.
        '''
        if self._lc.running:
            return
        else:
            self._lc.start(config.WAIT_INTERVAL)
            self.factory.running = True

    def _stop(self,*args):
        '''
        Stops the game and thanks people for playing,
        then saves the scores.
        '''
        if not self._lc.running:
            return
        else:
            self._lc.stop()
            self._gmsg('Thanks for playing trivia!')
            self._gmsg('Current rankings were:')
            self._standings(None,self._game_channel,None)
            self._gmsg('''Scores have been saved, and see you next game!''')
            self._save_game()
            self.factory.running = False

    def _save_game(self,*args):
        '''
        Saves the game to the data directory.
        '''
        if not path.exists(config.SAVE_DIR):
            makedirs(config.SAVE_DIR)
        with open(config.SAVE_DIR+'scores.json','w') as savefile:
            json.dump(self._scores, savefile)
            print "Scores have been saved."

    def _load_game(self):
        '''
        Loads the running data from previous games.
        '''
        # ensure initialization
        self._scores = {}
        if not path.exists(config.SAVE_DIR):
            print "Save directory doesn't exist."
            return
        try:
            with open(config.SAVE_DIR+'scores.json','r') as savefile:
                temp_dict = json.load(savefile)
        except:
            print "Save file doesn't exist."
            return
        for name in temp_dict.keys():
            self._scores[str(name)] = int(temp_dict[name])
        print self._scores
        print "Scores loaded."

    def _set_user_score(self, args, user, channel):
        '''
        Administrative action taken to adjust scores, if needed.
        '''
        try:
            self._scores[args[0]] = int(args[1])
        except:
            self._cmsg(user, args[0]+" not in scores database.")
            return
        self._cmsg(user, args[0]+" score set to "+args[1])

    def _die(self,*args):
        '''
        Terminates execution of the bot.
        Need to dig into twisted to figure out how this happens.
        '''
        global reactor
        self.quit(message='This is triviabot, signing off.')
        reactor.stop()
        # figure out how to kill the bot

    def _score(self,args,user,channel):
        '''
        Tells the user their score.
        '''
        try:
            self._cmsg(user, "Your current score is: %s" %
                       str(self._scores[user]))
        except:
            self._cmsg(user, "You aren't in my database.")

    def _next_question(self,args,user,channel):
        '''
        Administratively skips the current question.
        '''
        if not self._lc.running:
            self._gmsg("We are not playing right now.")
            return
        self._gmsg("Question has been skipped. The answer was: %s" %
                   self._answer.answer)
        self._clue_number = 0
        self._lc.stop()
        self._lc.start(config.WAIT_INTERVAL)

    def _standings(self,args,user,channel):
        '''
        Tells the user the complete standings in the game.

        TODO: order them.
        '''
        self._cmsg(user, "The current trivia standings are: ")
        sorted_scores = sorted(self._scores.iteritems(), key=lambda (k,v):
                               (v,k), reverse=True)
        for rank, (player, score) in enumerate(sorted_scores, start=1):
            formatted_score = "%s: %s: %s" % (rank,player,score)
            self._cmsg(user, str(formatted_score))

    def _give_clue(self,args,user,channel):
        if not self._lc.running:
            self._gmsg("we are not playing right now.")
            return
        self._cmsg(channel, "Question: ")
        self._cmsg(channel, self._question)
        self._cmsg(channel, "Clue: "+self._answer.current_clue())

    def _get_new_question(self):
        '''
        Selects a new question from the questions directory and
        sets it.
        '''
        damaged_question = True
        while damaged_question:
            #randomly select file
            filename = choice(listdir(self._questions_dir))
            fd = open(config.Q_DIR+filename)
            lines = fd.read().splitlines()
            myline = choice(lines)
            fd.close()
            try:
                self._question, temp_answer = myline.split('`')
            except ValueError:
                print "Broken question:"
                print myline
                continue
            self._answer.set_answer(temp_answer.strip())
            damaged_question = False

class ircbotFactory(ClientFactory):
    protocol = triviabot

    def __init__(self, nickname=config.DEFAULT_NICK):
        self.nickname = nickname
        self.running = False
        self.lineRate = config.LINE_RATE

    def clientConnectionLost(self, connector, reason):
        print("Lost connection (%s)" % (reason,))
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print("Could not connect: %s" % (reason,))
        connector.connect()


if __name__ == "__main__":
    # these two lines do the irc connection over ssl.
    reactor.connectSSL(config.SERVER, config.SERVER_PORT,
                       config.ircbotFactory(), ssl.ClientContextFactory())
    # reactor.connectTCP(config.SERVER, config.SERVER_PORT, ircbotFactory())
    reactor.run()
