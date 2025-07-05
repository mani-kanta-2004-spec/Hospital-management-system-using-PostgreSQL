import psycopg2
from datetime import datetime
from doctor import view_doctor_appointments

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



def view_room_assignments():
    try:
        print("\n=== Room Assignments ===")
        cursor.execute("""
            SELECT m.patient_id, p.name, m.room_id, m.admission_date, m.discharge_date 
            FROM patients p 
            JOIN manage_rooms m ON p.patient_id = m.patient_id
        """)
        room_assignments = cursor.fetchall()

        if room_assignments:
            for assignment in room_assignments:
                discharge_date = assignment[4] if assignment[4] else "Still admitted"
                print(f"Patient ID: {assignment[0]}, Name: {assignment[1]}, Room ID: {assignment[2]}, Admission Date: {assignment[3]}, Discharge Date: {discharge_date}")
        else:
            print("No room assignments found.")
    except Exception as e:
        print(f"Error while fetching room assignments: {str(e)}")
        conn.rollback()

def assign_room_to_patient():
    try:
        print("\n=== Assign Room to Patient ===")
        
        # Ask for the patient ID
        patient_id = input("Enter the Patient ID: ")

        # Show available rooms that are not occupied
        cursor.execute("SELECT room_id, room_number, room_type FROM room WHERE is_occupied = FALSE")
        available_rooms = cursor.fetchall()

        if not available_rooms:
            print("No rooms available!")
            return

        # Display the available rooms
        print("\nAvailable Rooms:")
        for room in available_rooms:
            print(f"Room ID: {room[0]}, Room Number: {room[1]}, Room Type: {room[2]}")

        # Ask for the room ID to assign
        room_id = input("Enter the Room ID to assign: ")

        # Check if the selected room is available
        cursor.execute("SELECT is_occupied FROM room WHERE room_id = %s", (room_id,))
        is_occupied = cursor.fetchone()

        if not is_occupied or is_occupied[0]:
            print(f"Room ID {room_id} is already occupied.")
            return

        # Record the admission date and mark the room as occupied
        admission_date = datetime.now()
        cursor.execute(
            "UPDATE room SET patient_id = %s, is_occupied = TRUE, admission_date = %s,discharge_date = NULL WHERE room_id = %s",
            (patient_id, admission_date, room_id)
        )
        conn.commit()

        print(f"Room {room_id} assigned to Patient ID {patient_id} successfully.")
    
    except Exception as e:
        print(f"Error during room assignment: {e}")
        conn.rollback()



def discharge_patient():
    try:
        print("\n=== Discharge Patient ===")
        
        # Ask for the patient ID
        patient_id = input("Enter the Patient ID: ")

        # Find the room currently occupied by the patient
        cursor.execute(
            "SELECT room_id, room_number, admission_date FROM room WHERE patient_id = %s AND is_occupied = TRUE",
            (patient_id,)
        )
        room_info = cursor.fetchone()

        if not room_info:
            print(f"No room found for Patient ID {patient_id} or patient has already been discharged.")
            return

        room_id = room_info[0]
        room_number = room_info[1]
        admission_date = room_info[2]

        # Record the discharge date and mark the room as unoccupied
        discharge_date = datetime.now()
        cursor.execute(
            "UPDATE room SET is_occupied = FALSE, discharge_date = %s WHERE room_id = %s AND patient_id = %s",
            (discharge_date, room_id, patient_id)
        )
        conn.commit()

        print(f"Patient ID {patient_id} has been successfully discharged from Room {room_number}.")
    
    except Exception as e:
        print(f"Error during patient discharge: {e}")
        conn.rollback()

# Function to view all room details
def view_all_room_details():
    try:
        print("\n=== Room Details ===")
        cursor.execute("""
            SELECT room_number, patient_id, admission_date, discharge_date,is_occupied,room_type
            FROM room
        """)
        room_details = cursor.fetchall()
        if room_details:
            for room in room_details:
                if room[4]:
                    status = "Still admitted"
                else:
                    status = "Patient is discharged"
                print(f"Room ID: {room[0]}, Patient ID: {room[1]}, Admission Date: {room[2]}, Room Type: {room[5]}, Status: {status}")
        else:
            print("No room details available.")

    except Exception as e:
        print(f"Error while fetching room details: {str(e)}")
        conn.rollback()
def search_patients_by_medicine():
    try:
        medicine_id = input("Enter the medicine ID: ")
        cursor.execute("""
            SELECT p.patient_id, p.name, ph.cost 
            FROM pharmacy ph 
            JOIN patients p ON ph.patient_id = p.patient_id
            WHERE ph.medicine_id = %s
        """, (medicine_id,))
        patients = cursor.fetchall()

        if patients:
            print(f"\nPatients who bought medicine with ID {medicine_id}:")
            for patient in patients:
                print(f"Patient ID: {patient[0]}, Name: {patient[1]}, Cost: {patient[2]}")
        else:
            print(f"No patients found for medicine ID {medicine_id}.")
    except Exception as e:
        print(f"Error while fetching patients: {str(e)}")
        conn.rollback()


# Function to search for all medicines bought by a patient using patient ID
def search_medicines_by_patient():
    try:
        patient_id = input("Enter the patient ID: ")
        cursor.execute("""
            SELECT ph.medicine_id, ph.cost 
            FROM pharmacy ph
            WHERE ph.patient_id = %s
        """, (patient_id,))
        medicines = cursor.fetchall()

        if medicines:
            print(f"\nMedicines bought by Patient ID {patient_id}:")
            for medicine in medicines:
                print(f"Medicine ID: {medicine[0]}, Cost: {medicine[1]}")
        else:
            print(f"No medicines found for Patient ID {patient_id}.")
    except Exception as e:
        print(f"Error while fetching medicines: {str(e)}")
        conn.rollback()


# Function to insert a new pharmacy record manually
def insert_pharmacy_record():
    try:
        medicine_id = input("Enter the medicine ID: ")
        patient_id = input("Enter the patient ID: ")
        doctor_id = input("Enter the doctor ID: ")
        cost = input("Enter the cost: ")

        cursor.execute("""
            INSERT INTO pharmacy (medicine_id, patient_id, doctor_id, cost)
            VALUES (%s, %s, %s, %s)
        """, (medicine_id, patient_id, doctor_id, cost))
        conn.commit()

        print("Pharmacy record inserted successfully.")
    except Exception as e:
        print(f"Error while inserting pharmacy record: {str(e)}")
        conn.rollback()


def get_room_details_by_patient():
    try:
        name = input("Enter your name: ")
        mobile_no = input("Enter your mobile number: ")

        # Check if the patient exists
        cursor.execute("SELECT * FROM patients WHERE name = %s AND mobile_no = %s", (name, mobile_no))
        patient = cursor.fetchone()
        patient_id = patient[0]

        if patient_id:
            # Fetch the room assignment for the patient
            cursor.execute("""
                SELECT room_number, admission_date, room_type
                FROM room
                WHERE patient_id = %s
            """, (patient_id,))
            room_details = cursor.fetchone()

            if room_details:
                discharge_date = room_details[2] if room_details[2] else "Still admitted"
                print(f"Room ID: {room_details[0]}, Admission Date: {room_details[1]}, room type: {room_details[2]}")
            else:
                print("No room assigned to the patient.")
        else:
            print("Patient not found. Cannot fetch room details.")
    except Exception as e:
        print(f"Error while fetching room details: {str(e)}")
        conn.rollback()


# Function for viewing all patients currently in the hospital
def view_current_patients():
    try:
        print("\n=== Current Patients ===")
        # Fetch patients regardless of room assignment for simplicity
        cursor.execute("SELECT patient_id, name, age, gender FROM patients")
        patients = cursor.fetchall()

        if patients:
            for patient in patients:
                print(f"Patient ID: {patient[0]}, Name: {patient[1]}, Age: {patient[2]}, Gender: {patient[3]}")
        else:
            print("No patients found in the system.")
    except Exception as e:
        print(f"Error while fetching current patients: {str(e)}")
        conn.rollback()

# Function to handle staff-specific actions
def staff_actions():
    try:
        role = input("Enter your role (Doctor, Nurse, Receptionist): ").lower()
        if role == "doctor":
            doctor_id = input("Enter your doctor ID: ")
            view_doctor_appointments(doctor_id)
        elif role == "nurse":
            view_current_patients()
        elif role == "receptionist":
            view_current_patients()
        else:
            print("Invalid role! Please enter Doctor, Nurse, or Receptionist.")
    except Exception as e:
        print(f"Error while handling staff actions: {str(e)}")
        conn.rollback()  # Rollback the transaction on error
def update_bills():
    try:
        print("\n=== Update Room and Medicine Bills ===")
        
        # Ask for the patient ID
        patient_id = input("Enter the Patient ID: ")

        # Check if there are any unpaid bills for the given patient
        cursor.execute("""
            SELECT bill_id, room_bill, medicine_bill, total_bill, status 
            FROM billing 
            WHERE patient_id = %s AND status = 'unpaid'
        """, (patient_id,))
        unpaid_bills = cursor.fetchall()

        # If no unpaid bills, inform the receptionist
        if not unpaid_bills:
            print(f"No unpaid bills found for Patient ID: {patient_id}.")
            return
        
        # Display unpaid bills
        print("\nUnpaid Bills:")
        for bill in unpaid_bills:
            print(f"Bill ID: {bill[0]}, Room Bill: {bill[1]}, Medicine Bill: {bill[2]}, Total Bill: {bill[3]}, Status: {bill[4]}")

        # Ask which bill to update
        bill_id = input("Enter the Bill ID to update: ")

        # Fetch the selected bill to update
        cursor.execute("SELECT room_bill, medicine_bill, total_bill FROM billing WHERE bill_id = %s", (bill_id,))
        bill = cursor.fetchone()

        if not bill:
            print(f"Bill ID {bill_id} not found!")
            return

        # Ask for the room and medicine bills
        new_room_bill = float(input(f"Enter the new room bill (current: {bill[0]}): "))
        new_medicine_bill = float(input(f"Enter the new medicine bill (current: {bill[1]}): "))

        # Calculate the new total bill
        new_total_bill = new_room_bill + new_medicine_bill + 500  # Appointment bill is fixed at 500

        # Update the bill in the database
        cursor.execute("""
            UPDATE billing 
            SET room_bill = %s, medicine_bill = %s, total_bill = %s 
            WHERE bill_id = %s
        """, (new_room_bill, new_medicine_bill, new_total_bill, bill_id))
        conn.commit()

        print(f"Bill updated successfully! New total bill: {new_total_bill}")

    except Exception as e:
        print(f"Error while updating bills: {str(e)}")
        conn.rollback()

def update_bill_status():
    try:
        print("\n=== Update Bill Status ===")
        
        # Ask for the patient ID
        patient_id = input("Enter the Patient ID: ")

        # Check if there are any unpaid bills for the given patient
        cursor.execute("""
            SELECT bill_id, total_bill, status 
            FROM billing 
            WHERE patient_id = %s
        """, (patient_id,))
        bills = cursor.fetchall()

        # If no bills found, inform the receptionist
        if not bills:
            print(f"No bills found for Patient ID: {patient_id}.")
            return

        # Display bills with their current status
        print("\nBills:")
        for bill in bills:
            print(f"Bill ID: {bill[0]}, Total Bill: {bill[1]}, Status: {bill[2]}")

        # Ask for the bill ID to update
        bill_id = input("Enter the Bill ID to update the status: ")

        # Fetch the selected bill
        cursor.execute("SELECT status FROM billing WHERE bill_id = %s", (bill_id,))
        bill = cursor.fetchone()

        if not bill:
            print(f"Bill ID {bill_id} not found!")
            return

        # Ask for the new status
        new_status = input(f"Enter the new status for Bill ID {bill_id} (current status: {bill[0]}): ").lower()
        if new_status not in ["paid", "unpaid"]:
            print("Invalid status! Please enter either 'paid' or 'unpaid'.")
            return

        # Update the status in the database
        cursor.execute("""
            UPDATE billing 
            SET status = %s 
            WHERE bill_id = %s
        """, (new_status, bill_id))
        conn.commit()

        print(f"Bill status updated successfully to {new_status}.")

    except Exception as e:
        print(f"Error while updating bill status: {str(e)}")
        conn.rollback()


def close_connection():
    cursor.close()
    conn.close()
    print("Database connection closed.")


  
