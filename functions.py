#!/usr/bin/env python
# 
# This is a trial file to test functions needed for the trivia bot.

def obscureAnswer(answer):
    oanswer = answer
    for i in range(len(answer)):
        if (oanswer[i] != '*'):
            oanswer = oanswer.replace(oanswer[i], '*')
    return oanswer



if __name__ == "__main__":
    import random
    answer = 'thirsty'
    lastanswer = obscureAnswer(answer)
    print(answer)
    print(lastanswer)
