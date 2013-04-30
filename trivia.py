#!/usr/bin/python2
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
from os import listdir,walk,path,makedirs
from random import randint,choice
from twisted.words.protocols import irc
from twisted.internet import ssl, reactor
from twisted.internet.protocol import ClientFactory, Protocol
from twisted.internet.task import LoopingCall
import json

from lib.answer import Answer

GAME_CHANNEL = '#trivia'
ADMINS = ['nameless']
Q_DIR = './questions/'
SAVE_DIR = './savedata/'
IDENT_STRING = 'oicu812'
WAIT_INTERVAL = 30
COLOR_CODE = 5

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
        self._admins = list(ADMINS)
        self._game_channel = GAME_CHANNEL
        self._current_points = 5
        self._questions_dir = Q_DIR
        self._lc = LoopingCall(self._play_game)
        self._load_game()

    def _get_nickname(self):
        return self.factory.nickname

    nickname = property(_get_nickname)

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
            self._get_new_question()
            self._current_points = points[self._clue_number]
            self.msg(self._game_channel,'')
            self.msg(self._game_channel, "Next question: ")
            self.msg(self._game_channel, self._question)
            self.msg(self._game_channel, 
                    "Clue: "+self._answer.current_clue())
            self._clue_number += 1
        # we must be somewhere in between
        elif self._clue_number < 4:
            self._current_points = points[self._clue_number]
            self.msg(self._game_channel, "Question: ")
            self.msg(self._game_channel, self._question)
            self.msg(self._game_channel,
                    'Clue: '+self._answer.give_clue())
            self._clue_number += 1
        # no one must have gotten it.
        else:
            self.msg(self._game_channel,
                '''No one got it. The answer was: '''
                +self._answer.answer)
            self._clue_number = 0
            self._get_new_question()
            #self._lc.reset()

    def signedOn(self):
        '''
        Actions to perform on signon to the server.
        '''
        self.join(self._game_channel)
        self.msg('NickServ','identify '+IDENT_STRING)
        print("Signed on as %s." % (self.nickname,))
        self.msg(self._game_channel,
                '''Welcome to '''+self._game_channel+'''!\n'''
                '''Have an admin start the game when you are ready.\n'''
                '''For how to use this bot, just say ? help or\n'''
                +self.nickname+' help.')

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
        while not msg[0].isalnum() and not msg[0] == '?':
            msg = msg[1:]

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
	    pass

    def _winner(self,user,channel):
        '''
        Congratulates the winner for guessing correctly and assigns
        points appropriately, then signals that it was guessed.
        '''
        self.msg(channel,user.upper()+" GUESSED IT!")
        try:
            self._scores[user] += self._current_points
        except:
            self._scores[user] = self._current_points
        if self._current_points == 1:
            self.msg(channel,str(self._current_points)+
                        " point has been added to your score!")
        else:
            self.msg(channel,str(self._current_points)+
                        " points have been added to your score!")
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
            self.msg(user,
                '''I'm nameless's trivia bot.\n'''
                '''Commands: score, standings, giveclue, help, source''')
            return
        self.msg(user,
            '''I'm nameless's trivia bot.\n'''
            '''Commands: score, standings, giveclue, help, source\n'''
            '''Admin commands: die, set <user> <score>, next, start,\n'''
            '''stop, save''')

    def _show_source(self,args,user,channel):
        '''
        Tells people how to use the bot.
        Only responds to the user since there could be a game in
        progress.
        '''
        self.msg(user,
            '''My source can be found at: '''
            '''https://github.com/rawsonj/triviabot''')

    def _color_test():
        self.msg(self._game_channel, str(COLOR_CODE)+
                '''This is a color test.''')

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
                                   'giveclue' : self._give_clue
                                 }
        priviledged_commands = { 'die' : self._die,
                                 'set' : self._set_user_score,
                                 'next': self._next_question,
                                 'start': self._start,
                                 'stop': self._stop,
                                 'save': self._save_game,
                                 'colortest': self._color_test
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
            self.msg(channel, user+": You don't tell me what to do.")
            return
        elif is_admin and priviledged_commands.has_key(command):
            priviledged_commands[command](args, user, channel)
        elif unpriviledged_commands.has_key(command):
            unpriviledged_commands[command](args, user, channel)
        else:
            self.describe(channel,'looks at '+user+' oddly.')
            
    def _start(self, args, user, channel):
        '''
        Starts the trivia game.

        TODO: Load scores from last game, if any.
        '''
        if self._lc.running:
            return
        else:
            self._lc.start(WAIT_INTERVAL)

    def _stop(self,*args):
        '''
        Stops the game and thanks people for playing,
        then saves the scores.
        '''
        if not self._lc.running:
            return
        else:
            self._lc.stop()
            self.msg(self._game_channel,
                    '''Thanks for playing trivia!\n'''
                    '''Current rankings were:\n'''
                    )
            self._standings(None,self._game_channel,None)
            self.msg(self._game_channel,
                    '''Scores have been saved, and see you next game!''')
            self._save_game()

    def _save_game(self,*args):
        '''
        Saves the game to the data directory.
        '''
        if not path.exists(SAVE_DIR):
            makedirs(SAVE_DIR)
        with open(SAVE_DIR+'scores.json','w') as savefile:
            json.dump(self._scores, savefile)
            print "Scores have been saved."

    def _load_game(self):
        '''
        Loads the running data from previous games.
        '''
        # ensure initialization
        self._scores = {}
        if not path.exists(SAVE_DIR):
            print "Save directory doesn't exist."
            return
        try:
            with open(SAVE_DIR+'scores.json','r') as savefile:
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
            self._scores[args[0]] = args[1]
        except:
            self.msg(user, args[0]+" not in scores database.")
            return
        self.msg(user, args[0]+" score set to "+args[1])

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
            self.msg(user,"Your current score is: "
                     +str(self._scores[user]))
        except:
            self.msg(user,"You aren't in my database.")

    def _next_question(self,args,user,channel):
        '''
        Administratively skips the current question.
        '''
        if not self._lc.running:
            self.msg(self._game_channel, "we are not playing right now.")
            return
        self.msg(self._game_channel,"Question has been skipped.")
        self._clue_number = 0
        self._lc.stop()
        self._lc.start(WAIT_INTERVAL)

    def _standings(self,args,user,channel):
        '''
        Tells the user the complete standings in the game.

        TODO: order them.
        '''
        self.msg(user,"The current trivia standings are: ")
        for name in self._scores.keys():
            self.msg(user,name+": "+str(self._scores[name]))

    def _give_clue(self,args,user,channel):
        if not self._lc.running:
            self.msg(self._game_channel, "we are not playing right now.")
            return
        self.msg(channel,"Question: ")
        self.msg(channel,self._question)
        self.msg(channel,"Clue: "+self._answer.current_clue())

    def _get_new_question(self):
        '''
        Selects a new question from the questions directory and
        sets it.
        '''
        damaged_question = True
        while damaged_question:
            #randomly select file
            filename = choice(listdir(self._questions_dir))
            fd = open(Q_DIR+filename)
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

    def __init__(self,nickname='trivia'):
        self.nickname = nickname

    def clientConnectionLost(self, connector, reason):
        print("Lost connection (%s)" % (reason,))
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print("Could not connect: %s" % (reason,))
        connector.connect()

    
if __name__ == "__main__":
    # these two lines do the irc connection over ssl.
    reactor.connectSSL('irc.cat.pdx.edu',6697,ircbotFactory(),ssl.ClientContextFactory())
    reactor.run()

