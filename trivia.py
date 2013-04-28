#!/usr/bin/python2
#
# I NEED AN ALGORITHM! :D
#
from random import randint,choice
from os import listdir,walk

class Answer:
    ''' 
    This class implements storage for an answer you want to conceil
    and give clues 1 letter at a time.

    Methods:

    giveClue(): returns the masked string after revealing a letter and saving the mask.
    getClue(): returns the masked string.
    setAnswer('string'): makes this object reusable, sets a new answer and clue mask.
    reveal(): returns the answer string. 
    '''
    
    def __init__(self, answer='None'):
        self._answer = answer
        self._masked_answer = str()

        for i in self._answer:
            if i.isalnum():
                self._masked_answer += '*'
            else:
                self._masked_answer += i

    def give_clue(self):
        if self._answer == self._maskedAnswer:
            return self._masked_answer

        letter = ' '

        while not letter.isalnum():
            index = randint(0, len(self._answer)-1)
            letter = self._answer[index]
            if self._masked_answer[index] == letter:
                letter = ' '

        temp = list(self._masked_answer)

        temp[index] = letter

        self._masked_answer = "".join(temp)

        return self._masked_answer

    def get_clue(self):
        return self._masked_answer

    def set_answer(self, new_answer):
        self.__init__(answer=new_answer)

    def _reveal():
        return self._answer

    answer = property(_reveal)

class triviabot(irc.IRCClient):
    '''
    This is the irc bot portion of the trivia bot.
    '''
    def __init__(self):
        self._answer = Answer()
        self._question = ''
        self._scores = {}
        self._clue_number = 0
        self._ADMINS = ['nameless']
        self._game_channel = '#trivia'
        self._current_points = 5
        self._questions_dir = './questions'

    def _get_nickname(self):
        return self.factory.nickname

    nickname = property(_get_nickname)

    def signedOn(self):
        self.join(self._game_channel)
        self.msg('NickServ','identify oicu812')
        #	self.join(self.factory.channel, 'catsonly')
        print("Signed on as %s." % (self.nickname,))

    def joined(self, channel):
        print("Joined %s." %(channel,))

    def privmsg(self, user, channel, msg):
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
                get_new_question()

    def winner(self,user,channel):
        self.msg(channel,user.toupper()+""" GUESSED IT!""")
        self.msg(channel,str(self._current_points)+" have been added\
                  to your score!")
        try:
            self._scores[user] += self._current_points
        except:
            self._scores[user] = self._current_points

        # need to figure out access control.
    def ctcpQuery(self, user, channel, msg):
        print("CTCP recieved: "+user+":"+channel+": "+msg[0][0]+" "+msg[0][1])

    def help(self,name,channel):
        self.msg(channel,
            '''
            I'm nameless's trivia bot.
            Commands: score, standings, give clue
            Admin commands: die, set <user> <score>, next
            ''')

    def die(self):
        self.quit()

    def score(self,user):
        self.msg(user,"Your current score is: "
                 +str(self._scores[user])

    def next(self):
        self.msg(channel,"Question has been skipped.")
        get_new_question()

    def standings(self,user):
        self.msg(user,"The current trivia standings are: ")
        for name in self._scores.keys():
            self.msg(user,name+": "+str(self._scores[name]))

    def give_clue(self,channel):
        self.msg(channel,self._answer.get_clue())

    def selectCommand(self, command, args, user, channel):
        if user.find('nameless') != 0:
            self.msg(channel,'Piss off, you don\'t tell me what to do.',maxlength)
            return
        if command=='++' and args[0].isalnum and args[1].isdigit:
            for _ in range(int(args[1])):
                self.karma(args[0],channel)
        elif command=='help':
            self.help(user,channel)
        elif command=='die':
            self.die()
        elif command=='give' and args[0] == 'clue':
            give_clue(channel)
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
        return rv


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
    question = ""

    # go get our list of questions
    list_generator = walk('./questions/')
    filelist = []
    for i in list_generator:
        filelist.append(i)
    filelist = filelist[0][2]
    for num,i in enumerate(filelist):
        filelist[num] = './questions/' + i
    #print(filelist)
    print(getQuestion(choice(filelist)))

    # these two lines do the irc connection over ssl.
    #reactor.connectSSL('irc.cat.pdx.edu',6697,ircbotFactory(),ssl.ClientContextFactory())
    #reactor.run()

