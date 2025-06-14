import random

WORDS = ["python", "computer", "programming", "hangman", "developer", "algorithm"]
MAX_ATTEMPTS = 7

def choose_word():
    """Selects a random word from the list."""
    return random.choice(WORDS)

def display_word(word, guessed_letters):
    """Displays the word with guessed letters revealed."""
    return "".join(letter if letter in guessed_letters else "_" for letter in word)

