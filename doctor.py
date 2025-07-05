import psycopg2
from datetime import datetime

# Database connection
try:
    conn = psycopg2.connect(
        dbname="hospital_database",
        user="postgres",
        password="mani@2004",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()
    print("Connected to the database successfully!")
except Exception as e:
    print(f"Failed to connect to the database: {str(e)}")
    exit(1)  # Exit if the connection fails

# View doctor appointments function
def view_doctor_appointments(doctor_id):
    try:
        print(f"\n=== Appointments for Doctor {doctor_id} ===")
        today = datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute(
            "SELECT * FROM appointments WHERE doctor_id = %s AND appointment_date::DATE = %s",
            (doctor_id, today)
        )
        appointments = cursor.fetchall()

        if appointments:
            for appointment in appointments:
                print(f"Appointment ID: {appointment[0]}, Patient ID: {appointment[1]}, Date: {appointment[3]}")
        else:
            print("No appointments for today.\n")
    except Exception as e:
        print(f"Error while fetching appointments: {str(e)}")
        conn.rollback()  # Rollback the transaction on error

def view_medical_records():
    try:
        print("\n=== View Medical Records ===")
        patient_id = input("Enter the patient ID or provide patient name and phone number to identify: ")
        
        # Check if patient_id is provided or find by name and phone
        if not patient_id.isdigit():
            name = input("Enter patient's name: ")
            mobile_no = input("Enter patient's phone number: ")
            cursor.execute("SELECT * FROM patients WHERE name = %s AND mobile_no = %s", (name, mobile_no))
            patient = cursor.fetchone()
            if not patient:
                print("Patient not found! Please check the details.")
                return
            patient_id = patient[0]  # Set patient_id to the found patient's ID

        cursor.execute("SELECT * FROM medical_records WHERE patient_id = %s", (patient_id,))
        records = cursor.fetchall()

        if records:
            print(f"\nMedical Records for Patient ID {patient_id}:")
            for record in records:
                print(f"Record ID: {record[0]}, Description: {record[2]}, Date: {record[3]}")
        else:
            print("No medical records found for this patient.")
    except Exception as e:
        print(f"Error while fetching medical records: {str(e)}")
        conn.rollback()  # Rollback the transaction on error
        
def add_medical_record():
    try:
        print("\n=== Add Medical Record ===")
        patient_id = input("Enter the patient ID or provide patient name and phone number to identify: ")
        
        # Check if patient_id is provided or find by name and phone
        if not patient_id.isdigit():
            name = input("Enter patient's name: ")
            mobile_no = input("Enter patient's phone number: ")
            cursor.execute("SELECT * FROM patients WHERE name = %s AND mobile_no = %s", (name, mobile_no))
            patient = cursor.fetchone()
            if not patient:
                print("Patient not found! Please check the details.")
                return
            patient_id = patient[0]  # Set patient_id to the found patient's ID

        description = input("Enter the medical record description: ")

        cursor.execute(
            "INSERT INTO medical_records (patient_id, description) VALUES (%s, %s)",
            (patient_id, description)
        )
        conn.commit()
        print("Medical record added successfully!\n")
    except Exception as e:
        print(f"Error while adding medical record: {str(e)}")
        conn.rollback()  # Rollback the transaction on error

        # Function to generate reports
def generate_report():
    try:
        print("\n=== Generate Report ===")
        doctor_id = input("Enter the doctor ID: ")
        
        cursor.execute("SELECT * FROM appointments WHERE doctor_id = %s", (doctor_id,))
        appointments = cursor.fetchall()

        if appointments:
            print(f"Appointments for Doctor ID {doctor_id}:")
            for appointment in appointments:
                print(f"Appointment ID: {appointment[0]}, Patient ID: {appointment[1]}, Date: {appointment[3]}")
        else:
            print("No appointments found for this doctor.")
    except Exception as e:
        print(f"Error while generating report: {str(e)}")
        conn.rollback()  # Rollback the transaction on error

# Close the connection when done
def close_connection():
    cursor.close()
    conn.close()
    print("Database connection closed.")

