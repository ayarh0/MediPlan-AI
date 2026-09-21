import sqlite3


DATABASE = "mediplan.db"


def get_connection():
    return sqlite3.connect(DATABASE)


def init_database():

    connection = get_connection()
    cursor = connection.cursor()

    # ==============================
    # MEDICATIONS TABLE
    # ==============================

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


    # ==============================
    # ALARMS TABLE
    # ==============================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alarms (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            medication_id INTEGER NOT NULL,

            alarm_time TEXT NOT NULL,

            days TEXT NOT NULL,

            enabled INTEGER DEFAULT 1,

            snooze_minutes INTEGER DEFAULT 10,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (medication_id)
            REFERENCES medications(id)

        )
    """)


    connection.commit()

    connection.close()