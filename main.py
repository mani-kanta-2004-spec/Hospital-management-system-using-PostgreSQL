import psycopg2
from doctor import view_doctor_appointments, add_medical_record, generate_report, close_connection, view_medical_records
from manager import recruit_staff, view_staff_details
from datetime import datetime, timedelta
from receptionist import view_current_patients, view_room_assignments, staff_actions,assign_room_to_patient,discharge_patient,update_bill_status, update_bills,view_all_room_details,get_room_details_by_patient,insert_pharmacy_record,search_medicines_by_patient,search_patients_by_medicine
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



# Create necessary tables if they don't exist
def create_tables():
    try:
        # Users table to store login information and roles
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
            CREATE TABLE IF NOT EXISTS pharmacy (
                medicine_id INT,
                patient_id INT REFERENCES patients(patient_id),
                doctor_id INT REFERENCES doctors(doctor_id),  -- Assuming doctor info comes from staff table
                cost INT,
                unique(medicine_id,patient_id)
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS manage_rooms (
                assignment_id SERIAL PRIMARY KEY,
                patient_id INT REFERENCES patients(patient_id),
                room_id INT,
                admission_date TIMESTAMP,
                discharge_date TIMESTAMP DEFAULT NULL
            );
        """)
        cursor.execute("""
           CREATE TABLE IF NOT EXISTS room (
                assignment_id SERIAL PRIMARY KEY,  -- Unique ID for each room assignment
                patient_id INT REFERENCES patients(patient_id) ON DELETE CASCADE, -- Reference to the patient assigned to the room
                room_id SERIAL,                    -- Unique ID for the room itself
                room_number VARCHAR(10) UNIQUE,    -- Room number (must be unique)
                room_type VARCHAR(20),             -- Room type (General, Private, ICU, etc.)
                is_occupied BOOLEAN DEFAULT FALSE, -- Room status (true if occupied, false if not)
                admission_date TIMESTAMP,          -- Date and time when the patient was admitted
                discharge_date TIMESTAMP           -- Date and time when the patient was discharged (nullable)
            );

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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS billing (
                bill_id SERIAL PRIMARY KEY,               -- Unique ID for each bill
                patient_id INT REFERENCES patients(patient_id) ON DELETE CASCADE,  -- Foreign key to patients table
                room_bill NUMERIC DEFAULT 0,              -- Room bill, default set to 0
                appointment_bill NUMERIC DEFAULT 500,     -- Appointment bill, set default as 500
                medicine_bill NUMERIC DEFAULT 0,          -- Medicine bill, default set to 0
                total_bill NUMERIC,                       -- Total bill, sum of room, appointment, and medicine bills
                status VARCHAR(20) DEFAULT 'unpaid',      -- Bill status: 'unpaid' or 'paid'
                billing_date DATE DEFAULT CURRENT_DATE    -- Date the bill was created, default is the current date
            );

        """)
        conn.commit()
        print("Tables created or verified successfully!")
    except Exception as e:
        print(f"Error while creating tables: {str(e)}")
        conn.rollback()

# Hash password for security
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Validate input (helper function)
def validate_input(input_str, input_type, options=None):
    if input_type == "int":
        try:
            return int(input_str)
        except ValueError:
            print("Invalid input! Please enter a valid number.")
            return None
    elif input_type == "date":
        try:
            return datetime.strptime(input_str, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format! Please enter in 'YYYY-MM-DD' format.")
            return None
    elif input_type == "time":
        try:
            return datetime.strptime(input_str, "%H:%M").time()
        except ValueError:
            print("Invalid time format! Please enter in 'HH:MM' format.")
            return None
    elif input_type == "choice":
        if input_str in options:
            return input_str
        else:
            print(f"Invalid choice! Please choose from {options}.")
            return None
    else:
        print("Invalid input type specified.")
        return None

# Login function
def login():
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    # Hash the entered password for comparison
    hashed_password = hash_password(password)

    cursor.execute("SELECT user_id, role FROM users WHERE username = %s AND password = %s", (username, hashed_password))
    user = cursor.fetchone()

    if user:
        print(f"Login successful! You are logged in as a {user[1]}.")
        return user[0], user[1]  # Return user_id and role
    else:
        print("Invalid username or password!")
        return None, None

# Function to register a new user (staff or patient)
def register_user(role):
    while True:
        username = input("Enter a username: ")
        
        # Check for unique username based on role
        cursor.execute("SELECT * FROM users WHERE username = %s AND role = %s", (username, role))
        existing_user = cursor.fetchone()

        if existing_user:
            print("Username already exists for this role. Please choose a different username.")
            continue  # Prompt for a new username

        password = input("Enter a password: ")
        hashed_password = hash_password(password)

        try:
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s) RETURNING user_id",
                (username, hashed_password, role)
            )
            user_id = cursor.fetchone()[0]
            conn.commit()
            print(f"User {username} registered successfully with role {role}. User ID: {user_id}")
            break  # Exit the loop after successful registration
        except Exception as e:
            print(f"Error registering user: {str(e)}")
            conn.rollback()
# Book appointment function for patients
def book_appointment():
    try:
        print("\n=== Book an Appointment ===")
        
        # Collect patient information
        name = input("Enter your name: ")
        mobile_no = input("Enter your mobile number: ")

        # Check if the patient exists
        cursor.execute("SELECT * FROM patients WHERE name = %s AND mobile_no = %s", (name, mobile_no))
        patient = cursor.fetchone()

        # If patient not found, create a new patient entry
        if not patient:
            print("Patient not found! A new patient ID will be created.")
            age = input("Enter your age: ")
            gender = input("Enter your gender: ")
            dob = input("Enter your date of birth (YYYY-MM-DD): ")

            cursor.execute(
                "INSERT INTO patients (name, age, gender, dob, mobile_no) VALUES (%s, %s, %s, %s, %s) RETURNING patient_id",
                (name, age, gender, dob, mobile_no)
            )
            patient_id = cursor.fetchone()[0]
            conn.commit()
            print(f"New patient ID created: {patient_id}")
        else:
            patient_id = patient[0]
            print(f"Patient ID found: {patient_id}")

        # Fetch available doctors
        cursor.execute("SELECT * FROM doctors")
        doctors = cursor.fetchall()

        if not doctors:
            print("No doctors available.")
            return

        print("\nAvailable Doctors:")
        for doctor in doctors:
            print(f"ID: {doctor[0]}, Name: {doctor[1]}, Specialization: {doctor[2]}")

        # Select a doctor
        doctor_id = input("Enter the Doctor ID you want to book an appointment with: ")
        cursor.execute("SELECT * FROM doctors WHERE doctor_id = %s", (doctor_id,))
        doctor = cursor.fetchone()
        if not doctor:
            print("Doctor not found! Please check the doctor ID.")
            return

        # Enter appointment date
        appointment_date_str = input("Enter the appointment date (YYYY-MM-DD): ")
        appointment_date = validate_input(appointment_date_str, "date")
        if not appointment_date:
            return
        
        # Generate time slots
        start_time = datetime.strptime("09:00", "%H:%M")
        end_time = datetime.strptime("16:00", "%H:%M")
        all_slots = []

        while start_time < end_time:
            all_slots.append(start_time.strftime("%H:%M"))
            start_time += timedelta(minutes=30)

        # Check available time slots for the selected doctor on the specified date
        cursor.execute("""
            SELECT appointment_date 
            FROM appointments 
            WHERE doctor_id = %s AND DATE(appointment_date) = %s
        """, (doctor_id, appointment_date.date()))
        booked_slots = [appointment[0].strftime("%H:%M") for appointment in cursor.fetchall()]
        
        available_slots = [slot for slot in all_slots if slot not in booked_slots]
        
        if not available_slots:
            print("No available slots for this date. Please choose another date.")
            return
        
        print(f"\nAvailable slots on {appointment_date_str}: {', '.join(available_slots)}")

        # Loop until user chooses a valid free slot
        while True:
            selected_time = input("Enter your preferred time (HH:MM): ")
            if selected_time not in available_slots:
                print(f"Slot {selected_time} is not available or invalid. Please choose from the available slots.")
            else:
                break
        
        # Combine date and time into a full datetime object
        appointment_datetime_str = f"{appointment_date_str} {selected_time}"
        appointment_datetime = datetime.strptime(appointment_datetime_str, "%Y-%m-%d %H:%M")

        # Book the appointment
        cursor.execute(
            "INSERT INTO appointments (patient_id, doctor_id, appointment_date) VALUES (%s, %s, %s)",
            (patient_id, doctor_id, appointment_datetime)
        )
        conn.commit()
        print(f"Appointment booked successfully on {appointment_datetime} with Doctor {doctor[1]}.")

        # After booking the appointment, create a billing entry for the patient
        cursor.execute(
            "INSERT INTO billing (patient_id, appointment_bill, total_bill) VALUES (%s, %s, %s)",
            (patient_id, 500, 500)  # Default appointment_bill is 500
        )
        conn.commit()
        print(f"Billing record created for Patient ID: {patient_id}. Total Bill: 500.")

    except Exception as e:
        print(f"Error while booking appointment: {str(e)}")
        conn.rollback()
# Function to view all room details


# View medical records function for patients
def view_medical_records_patient(patient_id):
    cursor.execute("SELECT * FROM medical_records WHERE patient_id = %s", (patient_id,))
    records = cursor.fetchall()
    if records:
        for record in records:
            print(f"Record: {record}")
    else:
        print("No medical records found for this patient.")

# Main menu function (role-based)
def main_menu(user_id, role):
    while True:
        print("\n=== Hospital Management System ===")
        
        # Menu options based on role
        if role == 'admin':
            print("1. View Staff Details")
            print("2. View Current Patients")
            print("3. Book Appointment for Patient")
            print("4. Add Medical Record")
            print("5. View Medical Records")
            print("6. Generate Report")
            print("7. View Room Assignments")
            print("8. Staff Actions")
            print("9. Recruitment")
            print("10. Assign Room to Patient")
            print("11. Discharge Patient")
            print("12. Update Bills")
            print("13. Update Bill Status")
            print("14. View All Room Details")
            print("15. View Patient Room Details")
            print("16. View Patient Pharmacy Records")
            print("17. Search Medicines by Patient")
            print("18. Update Pharma Records")
            print("0. Exit")
        elif role == 'patient':
            print("1. Book Appointment")
            print("2. View Medical Records")
            print("0. Exit")
        elif role == 'doctor':
            print("1. Add Medical Record")
            print("2. View Medical Records")
            print("3. Generate Report")
            print("0. Exit")
        elif role == 'pharmacy':
            print("1. Insert Pharmacy Record")
            print("2. Search Medicines by Patient")
            print("3. Search Patients by Medicine")
            print("0. Exit")
        elif role == 'nurse':
            print("1. View Current Patients")
            print("2. View Room Assignments")
            print("3. Assign Room to Patient")
            print("0. Exit")
        elif role == 'receptionist':
            print("1. View Staff Details")
            print("2. View Current Patients")
            print("3. Book Appointment")
            print("6. Generate Report")
            print("7. View Room Assignments")
            print("8. Staff Actions")
            print("10. Assign Room to Patient")
            print("11. Discharge Patient")
            print("12. Update Bills")
            print("13. Update Bill Status")
            print("14. View All Room Details")
            print("15. View Patient Room Details")
            print("16. View Patient Pharmacy Records")
            print("17. Search Medicines by Patient")
            print("18. Update Pharma Records")
            print("0. Exit")
        elif role == 'non_treating_staff':
            print("1. View Staff Details")
            print("2. View Current Patients")
            print("3. Book Appointment")
            print("6. Generate Report")
            print("7. View Room Assignments")
            print("8. Staff Actions")
            print("10. Assign Room to Patient")
            print("11. Discharge Patient")
            print("12. Update Bills")
            print("13. Update Bill Status")
            print("14. View All Room Details")
            print("15. View Patient Room Details")
            print("16. View Patient Pharmacy Records")
            print("17. Search Medicines by Patient")
            print("18. Update Pharma Records")
            print("0. Exit")
        
        choice = input("Enter your choice: ")
        choice = validate_input(choice, "int")
        
        if role == 'admin':
            if choice == 1:
                view_staff_details()
            elif choice == 2:
                view_current_patients()
            elif choice == 3:
                book_appointment()
            elif choice == 4:
                add_medical_record()
            elif choice == 5:
                view_medical_records()
            elif choice == 6:
                generate_report()
            elif choice == 7:
                view_room_assignments()
            elif choice == 8:
                staff_actions()
            elif choice == 9:
                recruit_staff()
            elif choice == 10:
                assign_room_to_patient()
            elif choice == 11:
                discharge_patient()
            elif choice == 12:
                update_bills()
            elif choice == 13:
                update_bill_status()
            elif choice == 14:
                view_all_room_details()
            elif choice == 15:
                get_room_details_by_patient()
            elif choice == 16:
                search_patients_by_medicine()
            elif choice == 17:
                search_medicines_by_patient()
            elif choice == 18:
                insert_pharmacy_record()
            elif choice == 0:
                print("Exiting the system. Goodbye!")
                break
            else:
                print("Invalid choice! Please select a valid option.")
        elif role == 'patient':
            if choice == 1:
                book_appointment()
            elif choice == 2:
                view_medical_records_patient(user_id)
            elif choice == 0:
                print("Exiting the system. Goodbye!")
                break
            else:
                print("Invalid choice! Please select a valid option.")
        elif role == 'doctor':
            if choice == 1:
                add_medical_record()
            elif choice == 2:
                view_medical_records()
            elif choice == 3:
                generate_report()
            elif choice == 0:
                print("Exiting the system. Goodbye!")
                break
            else:
                print("Invalid choice! Please select a valid option.")
        elif role == 'pharmacy':
            if choice == 1:
                insert_pharmacy_record()
            elif choice == 2:
                search_medicines_by_patient()
            elif choice == 3:
                search_patients_by_medicine()
            elif choice == 0:
                print("Exiting the system. Goodbye!")
                break
            else:
                print("Invalid choice! Please select a valid option.")
        elif role == 'nurse':
            if choice == 1:
                view_current_patients()
            elif choice == 2:
                view_all_room_details()
            elif choice == 3:
                assign_room_to_patient()
            elif choice == 0:
                print("Exiting the system. Goodbye!")
                break
            else:
                print("Invalid choice! Please select a valid option.")
        elif role == 'receptionist':
            if choice == 1:
                view_staff_details()
            elif choice == 2:
                view_current_patients()
            elif choice == 3:
                book_appointment()
            elif choice == 6:
                generate_report()
            elif choice == 7:
                view_room_assignments()
            elif choice == 8:
                staff_actions()
            elif choice == 10:
                assign_room_to_patient()
            elif choice == 11:
                discharge_patient()
            elif choice == 12:
                update_bills()
            elif choice == 13:
                update_bill_status()
            elif choice == 14:
                view_all_room_details()
            elif choice == 15:
                get_room_details_by_patient()
            elif choice == 16:
                search_patients_by_medicine()
            elif choice == 17:
                search_medicines_by_patient()
            elif choice == 18:
                insert_pharmacy_record()
            elif choice == 0:
                print("Exiting the system. Goodbye!")
                break
            else:
                print("Invalid choice! Please select a valid option.")
        elif role == 'non_treating_staff':
            if choice == 1:
                view_staff_details()
            elif choice == 2:
                view_current_patients()
            elif choice == 3:
                book_appointment()
            elif choice == 6:
                generate_report()
            elif choice == 7:
                view_room_assignments()
            elif choice == 8:
                staff_actions()
            elif choice == 10:
                assign_room_to_patient()
            elif choice == 11:
                discharge_patient()
            elif choice == 12:
                update_bills()
            elif choice == 13:
                update_bill_status()
            elif choice == 14:
                view_all_room_details()
            elif choice == 15:
                get_room_details_by_patient()
            elif choice == 16:
                search_patients_by_medicine()
            elif choice == 17:
                search_medicines_by_patient()
            elif choice == 18:
                insert_pharmacy_record()
            elif choice == 0:
                print("Exiting the system. Goodbye!")
                break
            else:
                print("Invalid choice! Please select a valid option.")
      
            

# Starting point for the program
# Starting point for the program
def start_program():
    create_tables()  # Create tables if they don't exist

    print("\nWelcome to the Hospital Management System!")
    print("1. Login")
    print("2. Register as Patient")
    print("3. Register as Staff")

    choice = validate_input(input("Enter your choice: "), "int")
    
    if choice == 1:
        user_id, role = login()
        if user_id:
            main_menu(user_id, role)
    elif choice == 2:
        register_user('patient')
    elif choice == 3:
        print("\nRegister as Staff:")
        print("1. Register as Doctor")
        print("2. Register as Receptionist")
        print("3. Register as Nurse")
        print("4. Register as Pharmacy")

        staff_choice = validate_input(input("Enter your choice: "), "int")
        if staff_choice == 1:
            register_user('doctor')
        elif staff_choice == 2:
            register_user('receptionist')
        elif staff_choice == 3:
            register_user('nurse')
        elif staff_choice == 4:
            register_user('Pharmacy')
        elif staff_choice ==5:
            register_user('admin')
        else:
            print("Invalid choice! Returning to main menu.")
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    start_program()



# Close the database connection at the end
cursor.close()
conn.close()