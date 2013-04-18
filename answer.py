
class Answer:
    
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
