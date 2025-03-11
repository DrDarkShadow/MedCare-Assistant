from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import sqlite3
import uuid
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# # Mount the "static" directory, where index.html is placed
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the frontend on /
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Update this variable to match your actual SQLite file path
DB_FILE = "hospital_db.sqlite3"

# Pydantic model for incoming appointment request data
class AppointmentRequest(BaseModel):
    name: str
    age: int
    gender: str
    contact_number: str
    email: str
    medical_history: str  # used as a filter for doctor's specialization
    appointment_date: str  # format: YYYY-MM-DD
    appointment_time: str  # format: HH:MM

# Pydantic model for the API response
class AppointmentResponse(BaseModel):
    message: str
    patient_id: str
    doctor_id: str = None
    doctor_name: str = None

@app.post("/api/book_appointment", response_model=AppointmentResponse)
def book_appointment(request_data: AppointmentRequest):
    # Connect to the SQLite database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Generate a unique 8-character patient ID
        patient_id = str(uuid.uuid4())[:8]
        
        # Insert new patient record into Patients table
        cursor.execute("""
            INSERT INTO Patients (patient_id, name, age, gender, contact_number, email, medical_history)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (patient_id, request_data.name, request_data.age, request_data.gender,
              request_data.contact_number, request_data.email, request_data.medical_history))
        conn.commit()
        
        # Look for doctors with a specialization matching the provided medical_history
        cursor.execute("""
            SELECT doctor_id, name FROM Doctors
            WHERE specialization = ?
        """, (request_data.medical_history,))
        doctors = cursor.fetchall()
        
        if not doctors:
            raise HTTPException(
                status_code=404,
                detail=f"No doctors found with specialization '{request_data.medical_history}'"
            )
        
        # Check each doctor to see if they are available at the given appointment date and time
        selected_doctor = None
        for doctor in doctors:
            doc_id, doc_name = doctor
            cursor.execute("""
                SELECT appointment_id FROM Appointments
                WHERE doctor_id = ? AND date = ? AND time = ?
            """, (doc_id, request_data.appointment_date, request_data.appointment_time))
            appointment = cursor.fetchone()
            if appointment is None:  # available if no appointment exists at that time
                selected_doctor = (doc_id, doc_name)
                break
        
        if not selected_doctor:
            raise HTTPException(
                status_code=404,
                detail="No doctor available at the given time. Please choose another date/time or doctor."
            )
        
        doctor_id, doctor_name = selected_doctor

        # Convert doctor_id to string
        doctor_id = str(doctor_id)
        
        # Insert the appointment into the Appointments table with status "Scheduled"
        department = request_data.medical_history  # using the medical_history as department/specialization
        cursor.execute("""
            INSERT INTO Appointments (patient_id, doctor_id, department, date, time, status)
            VALUES (?, ?, ?, ?, ?, 'Scheduled')
        """, (patient_id, doctor_id, department, request_data.appointment_date, request_data.appointment_time))
        conn.commit()
        
        return AppointmentResponse(
            message=f"Appointment scheduled with Dr. {doctor_name}",
            patient_id=patient_id,
            doctor_id=doctor_id,
            doctor_name=doctor_name
        )
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        conn.close()

# A simple health check endpoint
@app.get("/")
def read_root():
    return {"message": "Medical Chatbot API is running."}
