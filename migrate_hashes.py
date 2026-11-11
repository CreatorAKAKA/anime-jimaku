import sqlite3
import hashlib
from database import DB_PATH

with sqlite3.connect(DB_PATH) as conn:
    screenshots = conn.execute(
        "SELECT id, image FROM screenshots"
    ).fetchall()

    for screenshot_id, image_bytes in screenshots:
        image_hash = hashlib.sha256(image_bytes).hexdigest()

        conn.execute(
            "UPDATE screenshots SET image_hash = ? WHERE id = ?",
            (image_hash, screenshot_id)
        )

    print(f"Hashed {len(screenshots)} screenshots!")