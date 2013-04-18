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
            if i == ' ':
                self._maskedAnswer += ' '
            else:
                self._maskedAnswer += '*'

    def giveClue(self):
        from random import randint

        letter = ' '

        while letter == ' ':
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

def getQuestion(self,fd):
    from random import choice
    lines = fd.read().splitlines()
    myline = choice(lines)
    [self._question, temp] = myline.split('*')
    self._answer.setAnswer(temp)
    
if __name__ == "__main__":

    from os import walk

    question = ""
    
    # go get our list of questions
    list_generator = walk('./questions/')
    filelist = []
    for i in list_generator:
        filelist.append(i)
    filelist = filelist[0][2]
    #print(filelist)
