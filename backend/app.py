import os
import re
import sqlite3
from datetime import datetime

from flask import Flask, request, jsonify, send_from_directory

from database import init_database, get_connection


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)

# Initialize database
init_database()


# ============================================================
# FRONTEND
# ============================================================

@app.route("/")
def home():
    frontend_folder = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../frontend"
        )
    )

    return send_from_directory(
        frontend_folder,
        "index.html"
    )


# ============================================================
# LOCAL SYSTEM TIME
# ============================================================

@app.route("/local-time", methods=["GET"])
def get_local_time():

    now = datetime.now()

    return jsonify({
        "time": now.strftime("%H:%M"),
        "day": now.strftime("%a"),
        "date": now.strftime("%Y-%m-%d"),
        "datetime": now.strftime("%Y-%m-%d %H:%M:%S")
    })


# ============================================================
# HELPERS
# ============================================================

def is_valid_date(date_string):

    if not date_string:
        return True

    try:
        datetime.strptime(
            date_string,
            "%Y-%m-%d"
        )
        return True

    except ValueError:
        return False


def is_valid_time(time_string):

    if not time_string:
        return False

    pattern = r"^(?:[01]\d|2[0-3]):[0-5]\d$"

    return bool(
        re.match(
            pattern,
            time_string
        )
    )


def medication_exists(medication_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM medications
        WHERE id = ?
        """,
        (medication_id,)
    )

    result = cursor.fetchone()

    connection.close()

    return result is not None


# ============================================================
# MEDICATIONS - GET ALL
# ============================================================

@app.route("/medications", methods=["GET"])
def get_medications():

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            name,
            dosage,
            frequency,
            start_date,
            end_date
        FROM medications
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()

    medications = [
        dict(row)
        for row in rows
    ]

    connection.close()

    return jsonify(medications)


# ============================================================
# MEDICATIONS - GET ONE
# ============================================================

@app.route(
    "/medications/<int:medication_id>",
    methods=["GET"]
)
def get_medication(medication_id):

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            name,
            dosage,
            frequency,
            start_date,
            end_date
        FROM medications
        WHERE id = ?
        """,
        (medication_id,)
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:

        return jsonify({
            "error": "Medication not found."
        }), 404

    return jsonify(dict(row))


# ============================================================
# MEDICATIONS - CREATE
# ============================================================

@app.route("/medications", methods=["POST"])
def create_medication():

    data = request.get_json(silent=True)

    if not data:

        return jsonify({
            "error": "No JSON data received."
        }), 400

    name = str(
        data.get("name", "")
    ).strip()

    dosage = str(
        data.get("dosage", "")
    ).strip()

    frequency = str(
        data.get("frequency", "")
    ).strip()

    start_date = str(
        data.get("start_date", "")
    ).strip()

    end_date = str(
        data.get("end_date", "")
    ).strip()

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not name:

        return jsonify({
            "error": "Medication name is required."
        }), 400

    if len(name) > 150:

        return jsonify({
            "error": "Medication name is too long."
        }), 400

    if not is_valid_date(start_date):

        return jsonify({
            "error": "Invalid start date."
        }), 400

    if not is_valid_date(end_date):

        return jsonify({
            "error": "Invalid end date."
        }), 400

    if (
        start_date
        and end_date
        and end_date < start_date
    ):

        return jsonify({
            "error": "End date cannot be before start date."
        }), 400

    # --------------------------------------------------------
    # INSERT
    # --------------------------------------------------------

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO medications
        (
            name,
            dosage,
            frequency,
            start_date,
            end_date
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            name,
            dosage,
            frequency,
            start_date,
            end_date
        )
    )

    medication_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Medication created successfully.",
        "id": medication_id
    }), 201


# ============================================================
# MEDICATIONS - UPDATE
# ============================================================

@app.route(
    "/medications/<int:medication_id>",
    methods=["PUT"]
)
def update_medication(medication_id):

    data = request.get_json(silent=True)

    if not data:

        return jsonify({
            "error": "No JSON data received."
        }), 400

    name = str(
        data.get("name", "")
    ).strip()

    dosage = str(
        data.get("dosage", "")
    ).strip()

    frequency = str(
        data.get("frequency", "")
    ).strip()

    start_date = str(
        data.get("start_date", "")
    ).strip()

    end_date = str(
        data.get("end_date", "")
    ).strip()

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not name:

        return jsonify({
            "error": "Medication name is required."
        }), 400

    if not is_valid_date(start_date):

        return jsonify({
            "error": "Invalid start date."
        }), 400

    if not is_valid_date(end_date):

        return jsonify({
            "error": "Invalid end date."
        }), 400

    if (
        start_date
        and end_date
        and end_date < start_date
    ):

        return jsonify({
            "error": "End date cannot be before start date."
        }), 400

    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM medications
        WHERE id = ?
        """,
        (medication_id,)
    )

    existing = cursor.fetchone()

    if existing is None:

        connection.close()

        return jsonify({
            "error": "Medication not found."
        }), 404

    cursor.execute(
        """
        UPDATE medications
        SET
            name = ?,
            dosage = ?,
            frequency = ?,
            start_date = ?,
            end_date = ?
        WHERE id = ?
        """,
        (
            name,
            dosage,
            frequency,
            start_date,
            end_date,
            medication_id
        )
    )

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Medication updated successfully."
    })


# ============================================================
# MEDICATIONS - DELETE
# ============================================================

@app.route(
    "/medications/<int:medication_id>",
    methods=["DELETE"]
)
def delete_medication(medication_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM medications
        WHERE id = ?
        """,
        (medication_id,)
    )

    existing = cursor.fetchone()

    if existing is None:

        connection.close()

        return jsonify({
            "error": "Medication not found."
        }), 404

    # Delete alarms connected to medication
    cursor.execute(
        """
        DELETE FROM alarms
        WHERE medication_id = ?
        """,
        (medication_id,)
    )

    # Delete medication
    cursor.execute(
        """
        DELETE FROM medications
        WHERE id = ?
        """,
        (medication_id,)
    )

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Medication deleted successfully."
    })


# ============================================================
# ALARMS - GET ALL
# ============================================================

@app.route("/alarms", methods=["GET"])
def get_alarms():

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            medication_id,
            alarm_time,
            days,
            enabled,
            snooze_minutes,
            created_at
        FROM alarms
        ORDER BY alarm_time ASC
        """
    )

    rows = cursor.fetchall()

    alarms = [
        dict(row)
        for row in rows
    ]

    connection.close()

    return jsonify(alarms)


# ============================================================
# ALARMS - GET ONE
# ============================================================

@app.route(
    "/alarms/<int:alarm_id>",
    methods=["GET"]
)
def get_alarm(alarm_id):

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            medication_id,
            alarm_time,
            days,
            enabled,
            snooze_minutes,
            created_at
        FROM alarms
        WHERE id = ?
        """,
        (alarm_id,)
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:

        return jsonify({
            "error": "Alarm not found."
        }), 404

    return jsonify(dict(row))


# ============================================================
# ALARMS - CREATE
# ============================================================

@app.route("/alarms", methods=["POST"])
def create_alarm():

    data = request.get_json(silent=True)

    if not data:

        return jsonify({
            "error": "No JSON data received."
        }), 400

    medication_id = data.get(
        "medication_id"
    )

    alarm_time = str(
        data.get("alarm_time", "")
    ).strip()

    days = str(
        data.get("days", "")
    ).strip()

    enabled = data.get(
        "enabled",
        1
    )

    snooze_minutes = data.get(
        "snooze_minutes",
        10
    )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    try:

        medication_id = int(
            medication_id
        )

    except (
        TypeError,
        ValueError
    ):

        return jsonify({
            "error": "Invalid medication ID."
        }), 400

    if not medication_exists(
        medication_id
    ):

        return jsonify({
            "error": "Medication not found."
        }), 404

    if not is_valid_time(
        alarm_time
    ):

        return jsonify({
            "error": "Invalid alarm time."
        }), 400

    if not days:

        return jsonify({
            "error": "At least one day is required."
        }), 400

    try:

        enabled = (
            1
            if int(enabled)
            else 0
        )

    except (
        TypeError,
        ValueError
    ):

        enabled = 1

    try:

        snooze_minutes = int(
            snooze_minutes
        )

    except (
        TypeError,
        ValueError
    ):

        snooze_minutes = 10

    if snooze_minutes < 1:
        snooze_minutes = 1

    if snooze_minutes > 120:
        snooze_minutes = 120

    # --------------------------------------------------------
    # INSERT
    # --------------------------------------------------------

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO alarms
        (
            medication_id,
            alarm_time,
            days,
            enabled,
            snooze_minutes
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            medication_id,
            alarm_time,
            days,
            enabled,
            snooze_minutes
        )
    )

    alarm_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Alarm created successfully.",
        "id": alarm_id
    }), 201


# ============================================================
# ALARMS - UPDATE
# ============================================================

@app.route(
    "/alarms/<int:alarm_id>",
    methods=["PUT"]
)
def update_alarm(alarm_id):

    data = request.get_json(silent=True)

    if not data:

        return jsonify({
            "error": "No JSON data received."
        }), 400

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            medication_id,
            alarm_time,
            days,
            enabled,
            snooze_minutes
        FROM alarms
        WHERE id = ?
        """,
        (alarm_id,)
    )

    existing = cursor.fetchone()

    if existing is None:

        connection.close()

        return jsonify({
            "error": "Alarm not found."
        }), 404

    # --------------------------------------------------------
    # Existing values
    # --------------------------------------------------------

    medication_id = data.get(
        "medication_id",
        existing["medication_id"]
    )

    alarm_time = str(
        data.get(
            "alarm_time",
            existing["alarm_time"]
        )
    ).strip()

    days = str(
        data.get(
            "days",
            existing["days"]
        )
    ).strip()

    enabled = data.get(
        "enabled",
        existing["enabled"]
    )

    snooze_minutes = data.get(
        "snooze_minutes",
        existing["snooze_minutes"]
    )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    try:

        medication_id = int(
            medication_id
        )

    except (
        TypeError,
        ValueError
    ):

        connection.close()

        return jsonify({
            "error": "Invalid medication ID."
        }), 400

    if not medication_exists(
        medication_id
    ):

        connection.close()

        return jsonify({
            "error": "Medication not found."
        }), 404

    if not is_valid_time(
        alarm_time
    ):

        connection.close()

        return jsonify({
            "error": "Invalid alarm time."
        }), 400

    if not days:

        connection.close()

        return jsonify({
            "error": "At least one day is required."
        }), 400

    try:

        enabled = (
            1
            if int(enabled)
            else 0
        )

    except (
        TypeError,
        ValueError
    ):

        enabled = 1

    try:

        snooze_minutes = int(
            snooze_minutes
        )

    except (
        TypeError,
        ValueError
    ):

        snooze_minutes = 10

    if snooze_minutes < 1:
        snooze_minutes = 1

    if snooze_minutes > 120:
        snooze_minutes = 120

    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    cursor.execute(
        """
        UPDATE alarms
        SET
            medication_id = ?,
            alarm_time = ?,
            days = ?,
            enabled = ?,
            snooze_minutes = ?
        WHERE id = ?
        """,
        (
            medication_id,
            alarm_time,
            days,
            enabled,
            snooze_minutes,
            alarm_id
        )
    )

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Alarm updated successfully."
    })


# ============================================================
# ALARMS - DELETE
# ============================================================

@app.route(
    "/alarms/<int:alarm_id>",
    methods=["DELETE"]
)
def delete_alarm(alarm_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM alarms
        WHERE id = ?
        """,
        (alarm_id,)
    )

    existing = cursor.fetchone()

    if existing is None:

        connection.close()

        return jsonify({
            "error": "Alarm not found."
        }), 404

    cursor.execute(
        """
        DELETE FROM alarms
        WHERE id = ?
        """,
        (alarm_id,)
    )

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Alarm deleted successfully."
    })


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    ) 