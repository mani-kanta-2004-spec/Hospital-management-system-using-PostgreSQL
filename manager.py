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

def view_staff_details():
    while True:
        print("\n=== View Staff Details ===")
        staff_type = input("Choose staff type to view: (1) Doctors (2) Nurses (3) Non-Treating Staff (4) Exit: ")

        if staff_type == '1':
            print("\n=== Doctors ===")
            cursor.execute("SELECT d.doctor_id, e.name, e.mobile_no, e.address, e.salary FROM doctors d JOIN employees e ON d.employee_id = e.employee_id")
            doctors = cursor.fetchall()
            if doctors:
                for doctor in doctors:
                    print(f"Doctor ID: {doctor[0]}, Name: {doctor[1]}, Mobile: {doctor[2]}, Address: {doctor[3]}, Salary: {doctor[4]}")
            else:
                print("No doctors found.")

        elif staff_type == '2':
            print("\n=== Nurses ===")
            cursor.execute("SELECT n.nurse_id, e.name, e.mobile_no, e.address, e.salary FROM nurses n JOIN employees e ON n.employee_id = e.employee_id")
            nurses = cursor.fetchall()
            if nurses:
                for nurse in nurses:
                    print(f"Nurse ID: {nurse[0]}, Name: {nurse[1]}, Mobile: {nurse[2]}, Address: {nurse[3]}, Salary: {nurse[4]}")
            else:
                print("No nurses found.")

        elif staff_type == '3':
            print("\n=== Non-Treating Staff ===")
            cursor.execute("SELECT employee_id, name, mobile_no, address, salary FROM employees WHERE employee_id NOT IN (SELECT employee_id FROM doctors) AND employee_id NOT IN (SELECT employee_id FROM nurses)")
            non_treating_staff = cursor.fetchall()
            if non_treating_staff:
                for staff in non_treating_staff:
                    print(f"Staff ID: {staff[0]}, Name: {staff[1]}, Mobile: {staff[2]}, Address: {staff[3]}, Salary: {staff[4]}")
            else:
                print("No non-treating staff found.")

        elif staff_type == '4':
            break

        else:
            print("Invalid choice!")
            
def recruit_staff():
    print("\n=== Recruitment ===")
    role = input("Enter the role (Doctor, Nurse, Non-Treating Staff): ").strip().lower()

    if role == "doctor":
        name = input("Enter the doctor's name: ")
        mobile_no = input("Enter the doctor's mobile number: ")
        address = input("Enter the doctor's address: ")
        specialization = input("Enter the doctor's specialization: ")
        salary = input("Enter the doctor's salary: ")

        try:
            cursor.execute("INSERT INTO employees (name, mobile_no, address, salary) VALUES (%s, %s, %s, %s) RETURNING employee_id", 
                           (name, mobile_no, address, salary))
            employee_id = cursor.fetchone()[0]

            cursor.execute("INSERT INTO doctors (employee_id, specialization) VALUES (%s, %s)", 
                           (employee_id, specialization))

            conn.commit()
            print("Doctor recruited successfully!")

        except Exception as e:
            conn.rollback()
            print(f"Error during recruitment: {str(e)}")

    elif role == "nurse":
        name = input("Enter the nurse's name: ")
        mobile_no = input("Enter the nurse's mobile number: ")
        address = input("Enter the nurse's address: ")
        salary = input("Enter the nurse's salary: ")

        try:
            cursor.execute("INSERT INTO employees (name, mobile_no, address, salary) VALUES (%s, %s, %s, %s) RETURNING employee_id", 
                           (name, mobile_no, address, salary))
            employee_id = cursor.fetchone()[0]

            cursor.execute("INSERT INTO nurses (employee_id) VALUES (%s)", 
                           (employee_id,))

            conn.commit()
            print("Nurse recruited successfully!")

        except Exception as e:
            conn.rollback()
            print(f"Error during recruitment: {str(e)}")

    elif role == "non-treating staff":
        name = input("Enter the staff's name: ")
        mobile_no = input("Enter the staff's mobile number: ")
        address = input("Enter the staff's address: ")
        salary = input("Enter the staff's salary: ")

        try:
            cursor.execute("INSERT INTO employees (name, mobile_no, address, salary) VALUES (%s, %s, %s, %s) RETURNING employee_id", 
                           (name, mobile_no, address, salary))
            employee_id = cursor.fetchone()[0]

            # Non-Treating Staff doesn't have a separate table, just record it in employees.
            conn.commit()
            print("Non-Treating Staff recruited successfully!")

        except Exception as e:
            conn.rollback()
            print(f"Error during recruitment: {str(e)}")

    else:
        print("Invalid role! Please enter Doctor, Nurse, or Non-Treating Staff.")


    # Close the connection when done
def close_connection():
    cursor.close()
    conn.close()
    print("Database connection closed.")