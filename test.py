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
        score INTEGER,
        level TEXT
    )
""")
conn.commit()

def save_or_update_score(name, score, level):
    cursor.execute("SELECT * FROM scores WHERE name=?", (name,))
    existing_player = cursor.fetchone()

    if existing_player:
        new_score = existing_player[1] + score
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
    levels = {"easy": 50, "medium": 40, "hard": 20}
    level_attempts = {"easy": 8, "medium": 6, "hard": 4}

    level = input("Choose difficulty (easy, medium, hard): ").lower()
    if level not in levels:
        print("Invalid level, defaulting to medium.")
        level = "medium"

    total_words = levels[level]
    attempts = level_attempts[level]
    score = 0
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
                print(f"Exiting game. You scored {score}.")
                save_or_update_score(name, score, level)
                return

            if len(guess) != 1 or not guess.isalpha():
                print("Please enter a single letter.")
                continue

            if guess in guessed_letters:
                print("You've already guessed that letter.")
                continue

            if guess in word:
                guessed_letters.add(guess)
                print("Correct!")
            else:
                attempts -= 1
                print(f"Wrong! Attempts left: {attempts}")

            if all(letter in guessed_letters for letter in word):
                score += 5  # **Updated scoring: +5 points per correct word**
                print(f"\nYou guessed it! The word was '{word}'. Your score: {score}.")
                words_played += 1
                save_or_update_score(name, score, level)  # **Update scores live**
                attempts = level_attempts[level]  # Reset attempts for new word
                break  # Move to next word

        if attempts == 0:
            retry = input("You've lost! Do you want to retry this word? (yes/no): ").lower()
            if retry == "yes":
                attempts = level_attempts[level]  # Reset attempts for retry
                continue
            else:
                print(f"\nGame over! Your total score: {score}.")
                save_or_update_score(name, score, level)
                return

    print(f"\nYou finished level '{level}' with a score of {score}!")
    save_or_update_score(name, score, level)

    if level != "hard":
        next_level = {"easy": "medium", "medium": "hard"}
        proceed = input(f"Do you want to continue to {next_level[level]} level? (yes/no): ").lower()
        if proceed == "yes":
            play_guessing_game()

# Run the game
if __name__ == "__main__":
    play_guessing_game()