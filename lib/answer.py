from random import randrange

class Answer:
    '''
    This class implements storage for an answer you want to conceal
    and give clues 1 letter at a time.
    '''

    def __init__(self, answer='None'):
        self._answer = answer
	# TODO: This is a really inefficient way to go about doing this,
	# but I can't think of a good way to do this right now.
        self._masked_answer = str()
	self._unmasked = 0

        for character in self._answer:
            if character.isalnum():
                self._masked_answer += '*'
            else:
                self._masked_answer += character

    def give_clue(self):
	'''
	Returns the masked string after revealing a letter and saving the mask.

	If an answer has only 1-2 characters in it, no clues are given.

	If an answer has 3-4, 1 clue is given.

	If an answer has 5-6, 2 clues are given.
	'''
	# If all letters are unmasked, just return it.
        if self._answer == self._masked_answer:
            return self._masked_answer
	elif len(self) < 3:
	    return self._masked_answer
	elif len(self) < 5 and self._unmasked == 1:
	    return self._masked_answer
	elif len(self) < 7 and self._unmasked == 2:
	    return self._masked_answer

	# Choose the next letter to unmask.
	# Start with something to get us into the while loop.
        letter = ' '

	# If it's a symbol, choose a different letter.
        while not letter.isalnum():
	    # We need an index.
            index = randrange(0, len(self))
	    # Get the letter at that index from the answer.
            letter = self._answer[index]
	    # If the character was already unmasked, or is a symbol.
            if self._masked_answer[index] == letter:
                letter = ' '

	# Strings are immutable, so need to split and replace.
	self._masked_answer = self._masked_answer[:index] + letter + self._masked_answer[index + 1:]
	self._unmasked += 1

        return self._masked_answer

    def current_clue(self):
        return self._masked_answer

    def set_answer(self, new_answer):
	'''
	Sets a new answer string for the next question to use.
	'''
        self.__init__(answer=new_answer)

    def _reveal(self):
	'''
	Returns the unmasked answer string.
	'''
        return self._answer

    def __len__(self):
	return len(self._answer)

    answer = property(_reveal)
