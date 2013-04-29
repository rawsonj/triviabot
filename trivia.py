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
from time import sleep
import json

from lib.answer import Answer

GAME_CHANNEL = '#trivia'
ADMINS = ['nameless']
Q_DIR = './questions/'
SAVE_DIR = './triviabot_data'
IDENT_STRING = 'oicu812'
WAIT_INTERVAL = 5

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
        self._ADMINS = ADMINS
        self._game_channel = GAME_CHANNEL
        self._current_points = 5
        self._questions_dir = Q_DIR
        self._running = False
        self._got_it = False

    def _get_nickname(self):
        return self.factory.nickname

    nickname = property(_get_nickname)

    def signedOn(self):
        '''
        Actions to perform on signon to the server.
        '''
        self.join(self._game_channel)
        self.msg('NickServ','identify '+IDENT_STRING)
        print("Signed on as %s." % (self.nickname,))
        self.msg(self._game_channel,
                '''
                Welcome to '''+self._game_channel+'''!

                Have an admin start the game when you are ready.
                For how to use this bot, just say ? help or
                '''+self.nickname+' help.')

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
        print(user+" : "+channel+" : "+msg)
    # need to strip off colors if present.
        while not msg[0].isalnum() and not msg[0] == '?':
            msg = msg[1:]

    # parses each incoming line, and sees if it's a command for the bot.
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
            if msg == self._answer.answer:
                self._winner(user,channel)

    def _winner(self,user,channel):
        '''
        Congratulates the winner for guessing correctly and assigns
        points appropriately, then signals that it was guessed.
        '''
        self.msg(channel,user.toupper()+" GUESSED IT!")
        try:
            self._scores[user] += self._current_points
        except:
            self._scores[user] = self._current_points
        self.msg(channel,str(self._current_points)+
                    " have been added to your score!")
        self._got_it = True

    def _play_game(self):
        '''
        Implements the main loop of the game.
        '''
        self._get_new_question()
        while self._running:
            self._get_new_question()
            self._current_points = 5
            self._got_it = False
            self.msg(self._game_channel, "Next question:")
            self.msg(self._game_channel, self._question)
            self.msg(self._game_channel, 
                    "Clue: "+self._answer.current_clue())
            sleep(WAIT_INTERVAL)
            while not self._got_it:
                self.msg(self._game_channel, "Current question:")
                self.msg(self._game_channel, self._question)
                self.msg(self._game_channel,self._give_next_clue())
                sleep(WAIT_INTERVAL)

    def _give_next_clue(self):
        '''
        They didn't get it, so decrement the points and give the next
        clue.
        '''
        if self._current_points == 5:
            self._current_points -= 2
        elif self._current_points == 3:
            self._current_points -= 2
        elif self._current_points == 1:
            self._current_points -= 1
            self.msg(self._game_channel,
                    '''
                    No one got it. The answer was:
                    '''+self._answer.answer)
            self._got_it = True
            return
        self.msg(self._game_channel,
                'Clue: '+self._answer.give_clue())

        # need to figure out access control.
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
            self._ADMINS.index(user)
        except:
            self.msg(user,
                '''
                I'm nameless's trivia bot.
                Commands: score, standings, giveclue, help
                ''')
            return

        self.msg(name,
            '''
            I'm nameless's trivia bot.
            Commands: score, standings, giveclue, help
            Admin commands: die, set <user> <score>, next, start,
            stop, save
            ''')

    def select_command(self, command, args, user, channel):
        '''
        Callback that responds to commands given to the bot.

        Need to differentiate between priviledged users and regular
        users.
        '''
        # set up command dicts.
        unpriviledged_commands = { 'score': self._score
                                   'help' : self._help
                                   'standings' : self._standings
                                   'giveclue' : self._give_clue
                                 }
        priviledged_commands = { 'die' : self._die
                                 'set' : self._set_user_score
                                 'next': self._next_question
                                 'start': self._start
                                 'stop': self._stop
                                 'save': self._save
                               }
        try:
            self._ADMINS.index(user)
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
            
#        # start with user commands
#        if command== 'score':
#            self._score(user)
#        elif command=='help':
#            self._help(user,channel)
#        elif command=='standings':
#            self._standings(user)
#        elif command=='give' and args[0] == 'clue':
#            self._give_clue(channel)
#        elif is_admin:
#            if 
#            elif command=='set':
#            elif command=='die':
#                self._die()
#        else:
#            self.describe(channel,'looks at '+user+' oddly.')

    def _start(self, args, user, channel):
        '''
        Starts the trivia game.

        TODO: Load scores from last game, if any.
        '''
        if self._running:
            return
        else:
            self._running = True
            self._play_game()

    def _stop(self,args,user,channel):
        '''
        Stops the game and thanks people for playing,
        then saves the scores.
        '''
        if self._running == False:
            return
        else:
            self._running = False
            self._got_it = True
            self.msg(self._game_channel,
                    '''
                    Thanks for playing trivia!
                    '''
                    )
            self._save_game()

    def _save_game(self,args,user,channel):
        '''
        Saves the game to the data directory.
        '''
        pass

    def _load_game(self):
        '''
        Loads the running data from previous games.
        '''
        pass
------
    def _set_user_score(self, args, user, channel):
        '''
        Administrative action taken to adjust scores, if needed.
        '''
        try:
            self._scores[user] = score
        except:
            self.msg(admin, user+" not in scores database.")
            return
        self.msg(admin, user+" score set to "+score)

    def _die(self,args,user,channel):
        '''
        Terminates execution of the bot.
        Need to dig into twisted to figure out how this happens.
        '''
        #self.quit()
        # figure out how to kill the bot
        pass

    def _score(self,args,user,channel):
        '''
        Tells the user their score.
        '''
        self.msg(user,"Your current score is: "
                 +str(self._scores[user])

    def _next(self,args,user,channel):
        '''
        Administratively skips the current question.
        '''
        self.msg(self._game_channel,"Question has been skipped.")
        self._get_new_question()

    def _standings(self,args,user,channel):
        '''
        Tells the user the complete standings in the game.

        TODO: order them.
        '''
        self.msg(user,"The current trivia standings are: ")
        for name in self._scores.keys():
            self.msg(user,name+": "+str(self._scores[name]))

    def _give_clue(self,args,user,channel):
        self.msg(channel,"Clue: "+self._answer.current_clue())

    def _get_new_question(self):
        '''
        Selects a new question from the questions directory and
        sets it.
        '''
        #randomly select file
        filename = choice(listdir(self._questions_dir))
        fd = open(Q_DIR+filename)
        lines = fd.read().splitlines()
        myline = choice(lines)
        fd.close()
        self._question, temp_answer = myline.split('*')
        self._answer.set_answer(temp_answer)

class ircbotFactory(ClientFactory):
    protocol = bot

    def __init__(self,nickname='trivia'):
    #        self.channel = channel
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

