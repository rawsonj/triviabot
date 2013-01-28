#!/usr/bin/env python
#
# The core of the python trivia bot.
#
# I NEED AN ALGORITHM! :D
#
# I. Load a question and an answer.
#   A. Pick an entry at random from a file.
#   B. Load the question into a variable, load the answer
#       into another variable.
# II. Prepare to ask the question.
#   A. Create a blocked-out version of the answer as a clue.
# III. Ask the question, giving the clue.
#   A. Giving an amount of chances to answer the question,
#       ask the question, giving the clue. For each time
#       asked, choose a random letter from the answer and
#       create a new mask "revealing" that letter, in all
#       occurrances of that letter, in the position it occurs.
#       Cycle through until the amount of chances has been reached,
#       pausing for a set amount of time in between, and then
#       reveal the correct answer if the answer hasn't been
#       guessed yet.
# IV. When addressed, parse to take commands, match answers.
#   A. When addressed, parse for commands, else match for answer.
# V. Keep score.
#   A. For every nick who has successfully answered a question,
#       create an entry in an internal database, and keep track
#       of how many correct answers they have answered.

def getQuestion(fd,fLen):
    

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def getFilename():
    print("Please select a category.")

if __name__ == "__main__":
    
