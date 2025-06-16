import random
import sqlite3

# Define levels with words, max attempts, and hints
LEVELS = {
    1: {"words": {"cat": "An animal", "dog": "A pet", "hat": "Worn on the head", "sun": "A celestial body"},
        "max_attempts": 5},
    2: {"words": {"python": "A programming language", "computer": "An electronic device",
                  "developer": "A person who creates software", "keyboard": "Used for typing"},
        "max_attempts": 7},
    3: {"words": {"algorithm": "A set of rules in coding", "encryption": "Used for securing data",
                  "debugging": "Fixing coding errors", "framework": "A structured coding environment"},
        "max_attempts": 9},
}

DB_FILE = "game_scores.db"

def initialize_database(): 
    """Creates the database and scores table if not already present."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT,
            level INTEGER,
            completed_words TEXT,
            score INTEGER
        )
    """)
    conn.commit()
    conn.close()

def save_progress(player_name, level, completed_words, score):
    """Saves the player's progress in the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO scores (player_name, level, completed_words, score) VALUES (?, ?, ?, ?)",
                   (player_name, level, ",".join(completed_words), score))
    conn.commit()
    conn.close()

def load_progress(player_name):
    """Loads the player's progress if available."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT level, completed_words, score FROM scores WHERE player_name = ? ORDER BY id DESC LIMIT 1",
                   (player_name,)) # Fetch the latest progress
    result = cursor.fetchone()
    conn.close()
    
    if result:
        level = int(result[0]) 
        completed_words = result[1].split(",") if result[1] else [] # split 2nd item into a list
        score = int(result[2])
        return level, completed_words, score
    return None

def display_leaderboard():
    """Displays the leaderboard with sorted scores."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT player_name, level, score FROM scores ORDER BY score DESC")
    scores = cursor.fetchall()
    conn.close()

    print("\n=== LEADERBOARD ===")
    print(f"{'Rank':<5} {'Player Name':<15} {'Level':<7} {'Score':<7}") #left-align in a 5-character-wide column
    print("-" * 40)
    
    for rank, (name, level, score) in enumerate(scores, 1): #loops over the fetched scores,starting the rank from 1
        print(f"{rank:<5} {name:<15} {level:<7} {score:<7}") # prints each player's rank,name,level and score in aligned columns

def play_game():
    """Runs the Word Guessing Game with shuffled words, level selection, and progress saving."""
    initialize_database()
    player_name = input("Enter your name: ").title()
    
    progress = load_progress(player_name)
    if progress:
        level, completed_words, score = progress
        print(f"Welcome back, {player_name}! You are currently in **Level {level}**.")
    