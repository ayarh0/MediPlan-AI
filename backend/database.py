import sqlite3

DATABASE = "mediplan.db"


def get_connection():
    return sqlite3.connect(DATABASE)


def init_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dosage TEXT,
            frequency TEXT,
            start_date TEXT,
            end_date TEXT
        )
    """)

    connection.commit()
    connection.close()