import requests
import sqlite3

WORD_API_URL = "https://random-words-api.kushcreates.com/api"
DICT_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en"

# Database setup
conn = sqlite3.connect("game_scores.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS scores (
        name TEXT PRIMARY KEY,
        score INTEGER DEFAULT 0,
        level TEXT
    )
""")
conn.commit()

def save_or_update_score(name, score, level):
    cursor.execute("SELECT score, level FROM scores WHERE name=?", (name,))
    existing_player = cursor.fetchone()

    if existing_player:
        new_score = existing_player[0] + score
        cursor.execute("UPDATE scores SET score=?, level=? WHERE name=?", (new_score, level, name))
    else:
        cursor.execute("INSERT INTO scores (name, score, level) VALUES (?, ?, ?)", (name, score, level))

    conn.commit()

def get_word_with_hint():
    """Fetch a word with a valid hint."""
    while True:
        try:
            resp = requests.get(WORD_API_URL, params={"language": "en", "words": 1})
            resp.raise_for_status()
            word = resp.json()[0]["word"]
        except Exception as e:
            print(f"Failed to fetch word: {e}")
            return None, None

        try:
            dict_resp = requests.get(f"{DICT_API_URL}/{word}")
            dict_resp.raise_for_status()
            hint = dict_resp.json()[0]["meanings"][0]["definitions"][0]["definition"]
            if hint and isinstance(hint, str) and word.isalpha():
                return word.lower(), hint
        except Exception:
            continue  # Skip if no valid hint

def play_guessing_game():
    name = input("Enter your name: ")
    
    # Show current player score and level if returning player
    cursor.execute("SELECT score, level FROM scores WHERE name=?", (name,))
    existing_player = cursor.fetchone()
    if existing_player:
        print(f"Welcome back {name}! Current score: {existing_player[0]}, Level: {existing_player[1]}")
    
    levels = {"easy": 50, "medium": 40, "hard": 20}
    level_attempts = {"easy": 8, "medium": 6, "hard": 4}

    level = input("Choose difficulty (easy, medium, hard): ").lower()
    if level not in levels:
        print("Invalid level, defaulting to medium.")
        level = "medium"

    total_words = levels[level]
    attempts = level_attempts[level]
    score = existing_player[0] if existing_player else 0  # Keep score from previous sessions
    words_played = 0

    while words_played < total_words:
        word, hint = get_word_with_hint()
        if not word:
            print("Could not get a valid word and hint.")
            return

        guessed_letters = set()
        print(f"\nGuess the word! Attempts left: {attempts}")
        print(f"Hint: {hint}")
        print(f"The word has {len(word)} letters.\n")

        while attempts > 0:
            display = " ".join(letter if letter in guessed_letters else "_" for letter in word)
            print(f"Word: {display}")
            guess = input("Enter a letter (or 'exit' to quit): ").lower()

            if guess == "exit":
                print(f"Exiting game. Your score: {score}.")
                save_or_update_score(name, score, level)
                return

            