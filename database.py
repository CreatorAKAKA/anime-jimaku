import sqlite3
from pathlib import Path
import json
import hashlib

DB_PATH = Path(__file__).parent / "jimaquiz.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY,
                word TEXT NOT NULL UNIQUE,
                reading TEXT NOT NULL,
                meanings TEXT NOT NULL DEFAULT '[]'
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS screenshots (
                id INTEGER PRIMARY KEY,
                image BLOB NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS contexts (
                id INTEGER PRIMARY KEY,
                word_id INTEGER NOT NULL,
                screenshot_id INTEGER NOT NULL,
                sentence TEXT NOT NULL,
                surface TEXT NOT NULL,
                FOREIGN KEY (word_id) REFERENCES words(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (screenshot_id) REFERENCES screenshots(id)
            )
        """)

def save_word(word, reading, meanings):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO words (word, reading, meanings)
            VALUES (?, ?, ?)
            """,
            (word, reading, json.dumps(meanings, ensure_ascii=False))
        )

        cursor = conn.execute(
            "SELECT id FROM words WHERE word = ?",
            (word,)
        )
        return cursor.fetchone()[0]
        

def save_screenshot(image_bytes):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "INSERT INTO screenshots (image) VALUES (?)",
            (image_bytes,)
        )
        return cursor.lastrowid

def save_context(word_id, screenshot_id, sentence, surface):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            """
            INSERT INTO contexts
                (word_id, screenshot_id, sentence, surface)
            VALUES (?, ?, ?, ?)
            """,
            (word_id, screenshot_id, sentence, surface)
        )

def save_flashcard(word, reading, meanings, image_bytes, sentence, surface):
    word_id = save_word(word, reading, meanings)
    screenshot_id = save_screenshot(image_bytes)

    save_context(word_id, screenshot_id, sentence, surface)

def load_flashcards():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            SELECT
                words.word,
                words.reading,
                words.meanings,
                contexts.sentence,
                contexts.surface,
                screenshots.image
            FROM contexts
            JOIN words ON contexts.word_id = words.id
            JOIN screenshots ON contexts.screenshot_id = screenshots.id
        """)

        rows = cursor.fetchall()
        word_bank = {}

        for word, reading, meanings, sentence, surface, image in rows:
            if word not in word_bank:
                word_bank[word] = {
                    "reading": reading,
                    "meanings": json.loads(meanings),
                    "contexts": []
                }

            word_bank[word]["contexts"].append({
                "image_id": hashlib.sha256(image).hexdigest(),
                "image": image,
                "sentence": sentence,
                "surface": surface
            })

        return word_bank

if __name__ == "__main__":
    init_db()
    print("Database initialized!")
    save_word(
        "食べる",
        "たべる",
        [["to eat"], ["to consume"]]
    )