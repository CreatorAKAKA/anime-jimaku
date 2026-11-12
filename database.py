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
                image BLOB NOT NULL,
                image_hash TEXT NOT NULL UNIQUE
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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS collection_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS collection_sets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                FOREIGN KEY (group_id)
                    REFERENCES collection_groups(id)
                    ON DELETE CASCADE,
                UNIQUE(group_id, title)
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
    image_hash = hashlib.sha256(image_bytes).hexdigest()

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT id FROM screenshots WHERE image_hash = ?",
            (image_hash,)
        )

        existing = cursor.fetchone()

        if existing is not None:
            return existing[0]

        cursor = conn.execute(
            "INSERT INTO screenshots (image, image_hash) VALUES (?, ?)",
            (image_bytes, image_hash)
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

def update_context_sentences(image_bytes, corrected_text):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            UPDATE contexts
            SET sentence = ?
            WHERE screenshot_id IN (
                SELECT id FROM screenshots
                WHERE image = ?
            )
            """,
            (corrected_text, image_bytes)
        )

def delete_word(word):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            "DELETE FROM words WHERE word = ?",
            (word,)
        )
        conn.execute("""
            DELETE FROM screenshots
            WHERE NOT EXISTS (
                SELECT 1
                FROM contexts
                WHERE contexts.screenshot_id = screenshots.id
            )
        """)

def delete_context(word, image_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        # delete the specific context
        cursor = conn.execute("""
            DELETE FROM contexts
            WHERE word_id = (
                SELECT id FROM words WHERE word = ?
            )
            AND screenshot_id = (
                SELECT id FROM screenshots WHERE image_hash = ?
            )
        """, (word, image_id))

        # remove words with no remaining contexts
        conn.execute("""
            DELETE FROM words
            WHERE NOT EXISTS (
                SELECT 1 FROM contexts
                WHERE contexts.word_id = words.id
            )
        """)

        # remove screenshots with no remaining contexts
        conn.execute("""
            DELETE FROM screenshots
            WHERE NOT EXISTS (
                SELECT 1 FROM contexts
                WHERE contexts.screenshot_id = screenshots.id
            )
        """)


def create_group(name):
    """Create a new collection group."""
    name = name.strip()

    if not name:
        return

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO collection_groups (name) VALUES (?)",
            (name,)
        )


def create_set(group_id, title):
    """Create a new set inside a collection group."""
    title = title.strip()

    if not title:
        return

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            """
            INSERT OR IGNORE INTO collection_sets (group_id, title)
            VALUES (?, ?)
            """,
            (group_id, title)
        )


def load_groups():
    """Return groups and their sets from SQLite."""
    with sqlite3.connect(DB_PATH) as conn:
        groups = conn.execute(
            "SELECT id, name FROM collection_groups ORDER BY id"
        ).fetchall()

        result = []

        for group_id, name in groups:
            sets = conn.execute(
                """
                SELECT id, title
                FROM collection_sets
                WHERE group_id = ?
                ORDER BY id
                """,
                (group_id,)
            ).fetchall()

            result.append({
                "id": group_id,
                "name": name,
                "sets": [
                    {"id": set_id, "title": title}
                    for set_id, title in sets
                ]
            })

        return result

def delete_set(set_id):
    """Delete a collection set without deleting vocabulary."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            "DELETE FROM collection_sets WHERE id = ?",
            (set_id,)
        )

def rename_set(set_id, new_title):
    """Rename an existing set."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            UPDATE collection_sets
            SET title = ?
            WHERE id = ?
            """,
            (new_title, set_id)
        )

def move_set(set_id, new_group_id):
    """Move a set to another deck."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            UPDATE collection_sets
            SET group_id = ?
            WHERE id = ?
            """,
            (new_group_id, set_id)
        )

if __name__ == "__main__":
    init_db()
    print("Database initialized!")
    save_word(
        "食べる",
        "たべる",
        [["to eat"], ["to consume"]]
    )