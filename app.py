from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import uuid
from database import init_db, book_appointment, reschedule_appointment, cancel_appointment, get_appointments

app = Flask(__name__, template_folder='templates', static_folder='static')  # ✅ Ensure correct paths
CORS(app)  # Allow frontend requests
init_db()  # Initialize database

# 📌 Serve Frontend
@app.route('/')
def home():
    return render_template('index.html')  # ✅ Ensure 'index.html' exists inside the "templates" folder

# 📌 Book Appointment
@app.route('/api/book-appointment', methods=['POST'])
def book():
    data = request.json
    if not all([data.get(k) for k in ('name', 'age', 'gender', 'contact_number', 'email', 'medical_history', 'appointment_date', 'appointment_time')]):
        return jsonify({"error": "Missing data"}), 400

    result = book_appointment(data['name'], data['age'], data['gender'], data['contact_number'], data['email'], data['medical_history'], data['appointment_date'], data['appointment_time'])

    return jsonify(result), (400 if "error" in result else 200)

# 📌 Reschedule Appointment
@app.route('/api/reschedule-appointment', methods=['POST'])
def reschedule():
    data = request.json
    if not all([data.get(k) for k in ('name', 'old_date', 'old_time', 'new_date', 'new_time')]):
        return jsonify({"error": "Missing data"}), 400

    success = reschedule_appointment(data['name'], data['old_date'], data['old_time'], data['new_date'], data['new_time'])

    return jsonify({"message": "Appointment rescheduled"}) if success else jsonify({"error": "Appointment not found"}), 404

# 📌 Cancel Appointment
@app.route('/api/cancel-appointment', methods=['POST'])
def cancel():
    data = request.json
    if not all([data.get(k) for k in ('name', 'date', 'time')]):
        return jsonify({"error": "Missing data"}), 400

    success = cancel_appointment(data['name'], data['date'], data['time'])

    return jsonify({"message": "Appointment canceled"}) if success else jsonify({"error": "Appointment not found"}), 404

# 📌 Fetch All Appointments
@app.route('/api/appointments', methods=['GET'])
def list_appointments():
    return jsonify({"appointments": get_appointments()})

# 📌 Run Flask App
if __name__ == '__main__':
    app.run(debug=True)
