import sqlite3

DB_NAME = "database.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            clearance TEXT NOT NULL
        )
    """)

    users = [
        ("admin", "iuashd!@*#^*&^!HJAGDJuqbuoy18YGSUAGSDuh761623891", "Administrator", "ADMIN"),
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO users
        (username, password, role, clearance)
        VALUES (?, ?, ?, ?)
    """, users)

    conn.commit()
    conn.close()

    print("Database initialized successfully.")


if __name__ == "__main__":
    init_db()
