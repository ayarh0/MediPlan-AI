import os
from flask import Flask, request, jsonify, send_from_directory
from database import init_database, get_connection
app = Flask(__name__)

init_database()


@app.route("/")
def home():
    frontend_folder = os.path.join(os.path.dirname(__file__), "../frontend")
    return send_from_directory(frontend_folder, "index.html")  


@app.route("/medications", methods=["POST"])
def add_medication():
    data = request.get_json()

    name = data.get("name")
    dosage = data.get("dosage")
    frequency = data.get("frequency")
    start_date = data.get("start_date")
    end_date = data.get("end_date")

    if not name:
        return jsonify({"error": "Medication name is required"}), 400

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO medications
        (name, dosage, frequency, start_date, end_date)
        VALUES (?, ?, ?, ?, ?)
    """, (name, dosage, frequency, start_date, end_date))

    connection.commit()
    medication_id = cursor.lastrowid
    connection.close()

    return jsonify({
        "message": "Medication added successfully",
        "id": medication_id
    }), 201

@app.route("/medications", methods=["GET"])
def get_medications():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, dosage, frequency, start_date, end_date
        FROM medications
    """)

    medications = cursor.fetchall()
    connection.close()

    result = []

    for medication in medications:
        result.append({
            "id": medication[0],
            "name": medication[1],
            "dosage": medication[2],
            "frequency": medication[3],
            "start_date": medication[4],
            "end_date": medication[5]
        })

    return jsonify(result)
if __name__ == "__main__":
    app.run(debug=True) 