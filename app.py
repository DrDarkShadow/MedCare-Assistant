from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import uuid
from database import init_db, book_appointment, reschedule_appointment, cancel_appointment, get_appointments
from ai import extract_intent_and_details, collect_missing_details, process_request, convert_relative_date, convert_to_24hour_format, handle_web_request, check_missing_fields, process_web_request

app = Flask(__name__, template_folder='templates', static_folder='static')

# Modify CORS initialization
CORS(app, resources={r"/*": {"origins": "*"}})

init_db()

chat_history = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ai-response', methods=['POST'])
def ai_response():
    data = request.json
    user_input = data.get('message')

    # Step 1: Extract intent and details
    extracted_data = extract_intent_and_details(user_input)
    if not extracted_data or "intent" not in extracted_data:
        return jsonify({"error": "Couldn't understand request"}), 400

    intent = extracted_data["intent"]
    
    # Step 2: Check missing fields
    required_fields = {
        'book': ["name", "appointment_date", "appointment_time", "age", 
                "gender", "contact_number", "email", "department"],
        'reschedule': ["name", "old_date", "old_time", "new_date", "new_time"],
        'cancel': ["name", "appointment_date", "appointment_time"]
    }.get(intent, [])

    missing = [field for field in required_fields if not extracted_data.get(field)]
    
    # If missing fields, return them
    if missing:
        return jsonify({
            "missing_fields": missing,
            "current_state": extracted_data,
            "intent": intent
        })

    # Step 3: All fields present - process immediately
    try:
        if intent == "book":
            result = book_appointment(
                extracted_data["name"],
                extracted_data["age"],
                extracted_data["gender"],
                extracted_data["contact_number"],
                extracted_data.get("email", ""),
                extracted_data.get("department", ""),
                extracted_data["appointment_date"],
                extracted_data["appointment_time"]
            )
        elif intent == "reschedule":
            result = reschedule_appointment(
                extracted_data["name"],
                extracted_data["old_date"],
                extracted_data["old_time"],
                extracted_data["new_date"],
                extracted_data["new_time"]
            )
        elif intent == "cancel":
            result = cancel_appointment(
                extracted_data["name"],
                extracted_data["appointment_date"],
                extracted_data["appointment_time"]
            )
        else:
            return jsonify({"error": "Invalid intent"}), 400

        return jsonify({
            "message": f"Appointment {intent}ed successfully!",
            "appointment": result
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def check_missing_fields(data):
    intent = data.get('intent', 'book')
    required_fields = {
        'book': [
            'name', 'appointment_date', 'appointment_time',
            'age', 'gender', 'contact_number', 'email', 'department'
        ],
        'reschedule': [
            'name', 'old_date', 'old_time', 'new_date', 'new_time'
        ],
        'cancel': [
            'name', 'appointment_date', 'appointment_time'
        ],
        'view': []
    }.get(intent, [])
    
    return [field for field in required_fields if not data.get(field)]

@app.route('/api/book-appointment', methods=['POST'])
def book():
    data = request.json
    if not all([data.get(k) for k in ('name', 'age', 'gender', 'contact_number', 'email', 'medical_history', 'appointment_date', 'appointment_time')]):
        return jsonify({"error": "Missing data"}), 400
    result = book_appointment(data['name'], data['age'], data['gender'], data['contact_number'], data['email'], data['medical_history'], data['appointment_date'], data['appointment_time'])
    return jsonify(result), (400 if "error" in result else 200)

@app.route('/api/reschedule-appointment', methods=['POST'])
def reschedule():
    data = request.json
    if not all([data.get(k) for k in ('name', 'old_date', 'old_time', 'new_date', 'new_time')]):
        return jsonify({"error": "Missing data"}), 400
    success = reschedule_appointment(data['name'], data['old_date'], data['old_time'], data['new_date'], data['new_time'])
    return jsonify({"message": "Appointment rescheduled"}) if success else jsonify({"error": "Appointment not found"}), 404

@app.route('/api/cancel-appointment', methods=['POST'])
def cancel():
    data = request.json
    if not all([data.get(k) for k in ('name', 'date', 'time')]):
        return jsonify({"error": "Missing data"}), 400
    success = cancel_appointment(data['name'], data['date'], data['time'])
    return jsonify({"message": "Appointment canceled"}) if success else jsonify({"error": "Appointment not found"}), 404

@app.route('/api/appointments', methods=['GET'])
def list_appointments():
    return jsonify({"appointments": get_appointments()})

if __name__ == '__main__':
    app.run(debug=True)
