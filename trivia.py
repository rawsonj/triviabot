#!/usr/bin/env python
#
# I NEED AN ALGORITHM! :D
#

class Answer:
    ''' This class implements storage for an answer you want to conceil
    and give clues 1 letter at a time.

    Methods:

    giveClue(): returns the masked string after revealing a letter and saving the mask.
    getClue(): returns the masked string.
    setAnswer('string'): makes this object reusable, sets a new answer and clue mask.
    reveal(): returns the answer string. '''
    
    def __init__(self, answer):
        self._answer = answer
        self._maskedAnswer = str()

        for i in self._answer:
            if i.isalnum():
                self._maskedAnswer += '*'
            else:
                self._maskedAnswer += i

    def giveClue(self):
        if self._answer == self._maskedAnswer:
            return self._maskedAnswer
        from random import randint

        letter = ' '

        while not letter.isalnum():
            index = randint(0, len(self._answer)-1)
            letter = self._answer[index]
            if self._maskedAnswer[index] == letter:
                letter = ' '

        temp = list(self._maskedAnswer)

        temp[index] = letter

        self._maskedAnswer = "".join(temp)

        return self._maskedAnswer

    def getClue(self):
        return self._maskedAnswer

    def setAnswer(self, answer):
        self.__init__(answer)

    def reveal():
        return self._answer

class bot(irc.IRCClient):
    def _get_nickname(self):
        return self.factory.nickname

    nickname = property(_get_nickname)

    def signedOn(self):
        self.join('#trivia')
        self.msg('NickServ','identify oicu812')
        #	self.join(self.factory.channel, 'catsonly')
        print("Signed on as %s." % (self.nickname,))

    def joined(self, channel):
        print("Joined %s." %(channel,))

    def privmsg(self, user, channel, msg):
        print(user+" : "+channel+" : "+msg)
    # need to strip off colors if present.
    # need to figure out priviledged and non-priviledged commands
        while not msg[0].isalnum() and not msg[0] == '!':
            msg = msg[1:]

    # parses each incoming line, and sees if it's a command for the bot.
        if (msg[0]=="?"):
            command = msg.replace('?','').split()[0]
            args = msg.replace('?','').split()[1:]
        elif (msg.split()[0].find(self.nickname)==0):
            command = msg.split()[1]
            args = msg.replace(self.nickname,'').split()[2:]
        # if not, try to match the message to the answer.
        else:

        # need to figure out access control.
        if user.find('nameless') != 0:
            self.msg(channel,'Piss off, you don\'t tell me what to do.',maxlength)
            return
        self.selectCommand(command, args, user, channel)

    def ctcpQuery(self, user, channel, msg):
        print("CTCP recieved: "+user+":"+channel+": "+msg[0][0]+" "+msg[0][1])

    def karma(self,name,channel):
        self.msg(channel, name + "++",maxlength)

    def help(self,name,channel):
        self.msg(channel,
        '''I'm nameless's irc bot. I don't know much right now.
        Commands: ++ dance''')

    def die(self):
        self.quit()

    def selectCommand(self, command, args, user, channel):
        if command=='++' and args[0].isalnum and args[1].isdigit:
            for _ in range(int(args[1])):
                self.karma(args[0],channel)
        elif command=='dance':
            self.describe(channel,'does a little dance. (Like a zombie. Its disturbing.)')
        elif command=='help':
            self.help(user,channel)
        elif command=='die':
            self.die()
        else:
            self.describe(channel,'looks at you oddly.')

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

def getQuestion(filename):
    fd = open(filename)
    from random import choice
    lines = fd.read().splitlines()
    myline = choice(lines)
    rv = myline.split('*')
    return rv

    
if __name__ == "__main__":

    from os import walk
    from random import choice

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

