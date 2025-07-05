import psycopg2
from doctor import view_doctor_appointments, add_medical_record, generate_report, close_connection, view_medical_records
from manager import recruit_staff, view_staff_details
from datetime import datetime, timedelta
from receptionist import view_current_patients, view_room_assignments, staff_actions,assign_room_to_patient,discharge_patient
import hashlib

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

# Function to create tables if they don't exist
def create_tables(cursor):
    try:
        # Create employees table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                employee_id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                mobile_no VARCHAR(15),
                address TEXT,
                city VARCHAR(100),
                department VARCHAR(100),
                salary DECIMAL(10, 2)
            )
        """)

        # Create patients table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                patient_id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                mobile_no VARCHAR(15),
                address TEXT,
                city VARCHAR(100),
                age INT,
                gender VARCHAR(10)
            )
        """)

        # Create doctors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                doctor_id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                specialization VARCHAR(100)
            )
        """)

        # Create rooms table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                room_id SERIAL PRIMARY KEY,
                type VARCHAR(50),
                capacity INT
            )
        """)

        # Create assigned table to map patients to rooms
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assigned (
                patient_id INT REFERENCES patients(patient_id),
                room_id INT REFERENCES rooms(room_id),
                PRIMARY KEY (patient_id, room_id)
            )
        """)

        # Create appointments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                appointment_id SERIAL PRIMARY KEY,
                patient_id INT REFERENCES patients(patient_id),
                doctor_id INT REFERENCES doctors(doctor_id),
                appointment_date TIMESTAMP
            )
        """)

        # Create medical records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medical_records (
                record_id SERIAL PRIMARY KEY,
                patient_id INT REFERENCES patients(patient_id),
                description TEXT,
                record_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                username VARCHAR(100) NOT NULL,
                password VARCHAR(100) NOT NULL,
                role VARCHAR(20) NOT NULL, -- 'patient' or 'staff'
                UNIQUE (username, role)
            );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS manage_rooms (
            assignment_id SERIAL PRIMARY KEY,
            patient_id INT REFERENCES patients(patient_id),
            room_id INT,
            admission_date TIMESTAMP,
            discharge_date TIMESTAMP DEFAULT NULL
        );s
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stafflogin (
                user_id SERIAL PRIMARY KEY,
                username VARCHAR(100) NOT NULL,
                password VARCHAR(100) NOT NULL,
                role VARCHAR(100) NOT NULL,
                UNIQUE (username, role)
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nurses (
                nurse_id SERIAL PRIMARY KEY,
                employee_id INT REFERENCES employees(employee_id)
            );
        """)

        print("Tables created successfully!")
    except Exception as e:
        print(f"Error while creating tables: {str(e)}")



cursor = conn.cursor()

# Create the tables
create_tables(cursor)

print("Connected to the database and ensured tables exist!")