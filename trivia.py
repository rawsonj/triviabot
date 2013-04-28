#!/usr/bin/python2
#
# I NEED AN ALGORITHM! :D
#
from os import listdir,walk,path,makedirs
from random import randint,choice
from time import sleep
import json

from lib.answer import Answer

GAME_CHANNEL = '#trivia'
ADMINS = ['nameless']
Q_DIR = './questions'
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
        #	self.join(self.factory.channel, 'catsonly')
        print("Signed on as %s." % (self.nickname,))
        self.msg(self._game_channel,'''
                Welcome to '''+self._game_channel+'''!

                Have an admin start the game when you are ready.
                For how to use this bot, just say ? help or
                '''+self.nickname+''' help.'''

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

    # need to figure out priviledged and non-priviledged commands

    # parses each incoming line, and sees if it's a command for the bot.
        if (msg[0]=="?"):
            command = msg.replace('?','').split()[0]
            args = msg.replace('?','').split()[1:]
            self.selectCommand(command, args, user, channel)
            return
        elif (msg.split()[0].find(self.nickname)==0):
            command = msg.split()[1]
            args = msg.replace(self.nickname,'').split()[2:]
            self.selectCommand(command, args, user, channel)
            return
        # if not, try to match the message to the answer.
        else:
            if msg == self._answer.answer:
                winner(user,channel)
                self._got_it = True

    def _winner(self,user,channel):
        '''
        Congratulates the winner for guessing correctly and assigns
        points appropriately.
        '''
        self.msg(channel,user.toupper()+""" GUESSED IT!""")
        self.msg(channel,str(self._current_points)+" have been added\
                  to your score!")
        try:
            self._scores[user] += self._current_points
        except:
            self._scores[user] = self._current_points

        # need to figure out access control.
    def ctcpQuery(self, user, channel, msg):
        '''
        Responds to ctcp requests.
        Currently just reports them.
        '''
        print("CTCP recieved: "+user+":"+channel+": "+msg[0][0]+" "+msg[0][1])

    def _help(self,name,channel):
        '''
        Tells people how to use the bot.
        Replies differently if you are an admin or a regular user.
        Only responds to the user since there could be a game in
        progress.
        '''
        try:
            self._ADMINS.index(name)
        except:
            self.msg(name,
                '''
                I'm nameless's trivia bot.
                Commands: score, standings, give clue
                ''')
            return

        self.msg(name,
            '''
            I'm nameless's trivia bot.
            Commands: score, standings, give clue
            Admin commands: die, set <user> <score>, next, start,
            stop, save
            ''')

    def _start(self):
        self._running = True
        self.play_game()

    def _stop(self):
        pass

    def _save(self):
        pass

    def _set_user_score(self, channel, user, score):
        pass

    def _play_game(self):
        '''
        Implements the main loop of the game.
        '''
        self.get_new_question()
        while self._running:
            self.get_new_question()
            self._current_points = 5
            self.msg(self._game_channel, "Next question:")
            self.msg(self._game_channel, self._question)
            self.msg(self._game_channel, "Clue: \
                    "+self._answer.get_clue())
            sleep(WAIT_INTERVAL)
            while not self._got_it:
                sleep(WAIT_INTERVAL)
                self._give_next_clue()

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
        self.msg(self._game_channel, 'Clue: \
                '+self._answer.give_clue())

    def _die(self):
        self.quit()

    def _score(self,user):
        self.msg(user,"Your current score is: "
                 +str(self._scores[user])

    def _next(self):
        self.msg(channel,"Question has been skipped.")
        get_new_question()

    def _standings(self,user):
        self.msg(user,"The current trivia standings are: ")
        for name in self._scores.keys():
            self.msg(user,name+": "+str(self._scores[name]))

    def _give_clue(self,channel):
        self.msg(channel,self._answer.get_clue())

    def selectCommand(self, command, args, user, channel):
        if user.find('nameless') != 0:
            self.msg(channel,'Piss off, you don\'t tell me what to do.',maxlength)
            return
        if command=='++' and args[0].isalnum and args[1].isdigit:
            for _ in range(int(args[1])):
                self._karma(args[0],channel)
        elif command=='help':
            self._help(user,channel)
        elif command=='die':
            self._die()
        elif command=='give' and args[0] == 'clue':
            _give_clue(channel)
        else:
            self.describe(channel,'looks at '+user+' oddly.')

    def get_new_question(self):
        '''
        Selects a new question from the questions directory and
        returns [question, answer]
        '''
        #randomly select file
        filename = choice(listdir(self._questions_dir))
        fd = open(filename)
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
    # go get our list of questions
    list_generator = walk('./questions/')
    filelist = []
    for i in list_generator:
        filelist.append(i)
    filelist = filelist[0][2]
    print(getQuestion(choice(filelist)))

    # these two lines do the irc connection over ssl.
    #reactor.connectSSL('irc.cat.pdx.edu',6697,ircbotFactory(),ssl.ClientContextFactory())
    #reactor.run()

