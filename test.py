import requests
import sqlite3

# API endpoints for random words and definitions
WORD_API_URL = "https://random-words-api.kushcreates.com/api"
DICT_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en"

# Database setup to store player scores and levels
conn = sqlite3.connect("game_scores.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS scores (
        name TEXT PRIMARY KEY,  # Unique player name
        score INTEGER DEFAULT 0,  # Accumulated score
        level TEXT  # Current level of the player
    )
""")
conn.commit()

# Function to save or update player scores in the database
def save_or_update_score(name, score, level):
    cursor.execute("SELECT score, level FROM scores WHERE name=?", (name,))
    existing_player = cursor.fetchone()

    if existing_player:  # If player exists, update their score
        new_score = existing_player[0] + score
        cursor.execute("UPDATE scores SET score=?, level=? WHERE name=?", (new_score, level, name))
    else:  # Otherwise, insert new player record
        cursor.execute("INSERT INTO scores (name, score, level) VALUES (?, ?, ?)", (name, score, level))

    conn.commit()

# Function to fetch a random word and its definition as a hint
def get_word_with_hint():
    while True:
        try:
            # Fetch a random word from the API
            resp = requests.get(WORD_API_URL)
            resp.raise_for_status()
            word = resp.json()[0]["word"]  # Extract the word
        except Exception as e:
            print(f"Failed to fetch word: {e}")
            return None, None  # Handle errors gracefully

        try:
            # Fetch the definition of the word as a hint
            dict_resp = requests.get(f"{DICT_API_URL}/{word}")
            dict_resp.raise_for_status()
            hint = dict_resp.json()[0]["meanings"][0]["definitions"][0]["definition"]
            if hint and isinstance(hint, str) and word.isalpha():  # Ensure valid hint and word format
                return word.lower(), hint
        except Exception:
            continue  # Skip invalid words if an error occurs

# Function to play the guessing game
def play_guessing_game():
    name = input("Enter your name: ")

    # Check if the player exists in the database
    cursor.execute("SELECT score, level FROM scores WHERE name=?", (name,))
    existing_player = cursor.fetchone()
    score = existing_player[0] if existing_player else 0  # Retrieve previous score if available
    level = existing_player[1] if existing_player else "easy"  # Default to easy if new player

    print(f"\nWelcome back {name}! Current score: {score}, Level: {level}")

    # Define levels with word count and attempts
    levels = {"easy": 50, "medium": 40, "hard": 20}
    level_attempts = {"easy": 8, "medium": 6, "hard": 4}

    total_words = levels[level]  # Get the word count for selected level
    attempts = level_attempts[level]  # Get allowed attempts per word
    words_played = 0  # Track words played in the level

    while words_played < total_words:
        word, hint = get_word_with_hint()
        if not word:
            print("Could not get a valid word and hint.")
            return

        guessed_letters = set()  # Track guessed letters
        print(f"\nGuess the word! Attempts left: {attempts}")
        print(f"Hint: {hint}")
        print(f"The word has {len(word)} letters.\n")

        while attempts > 0:
            # Display the word with guessed letters
            display = " ".join(letter if letter in guessed_letters else "_" for letter in word)
            print(f"Word: {display}")
            guess = input("Enter a letter (or 'exit' to quit): ").lower()

            if guess == "exit":  # Exit the game
                print(f"\nExiting game. Your score: {score}.")
                save_or_update_score(name, score, level)
                return

            if len(guess) != 1 or not guess.isalpha():  # Ensure valid single-letter input
                print("Please enter a single letter.")
                continue

            if guess in guessed_letters:  # Prevent duplicate guesses
                print("You've already guessed that letter.")
                continue

            if guess in word:  # If guess is correct
                guessed_letters.add(guess)
                print("Correct!")
            else:  # Incorrect guess reduces attempts
                attempts -= 1
                print(f"Wrong! Attempts left: {attempts}")

            