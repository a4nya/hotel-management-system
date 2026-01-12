import pymysql
from datetime import date

try:
    con = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="hotel"
    )
    cur = con.cursor()
    print("Connected to database")
except pymysql.MySQLError as e:
    print("Database connection failed:", e)
    exit()

def admin_login():
    u = input("Username: ")
    p = input("Password: ")

    cur.execute(
        "SELECT * FROM admin WHERE username=%s AND password=%s",
        (u, p) )

    if cur.fetchone():
        print("Login successful")
        menu()
    else:
        print("Invalid login")
def get_room_details(room_no):
    first_digit = int(str(room_no)[0])

    if first_digit == 1:
        return "AC", 2000
    elif first_digit == 2:
        return "NON-AC", 1500
    elif first_digit == 3:
        return "DELUXE", 3000
    else:
        return None, None

def add_customer():
    cid = int(input("Customer ID: "))
    name = input("Name: ")
    phone = input("Phone: ")
    room_no = int(input("Room Number: "))
    today = date.today()

    room_type, price = get_room_details(room_no)

    if room_type is None:
        print("Invalid room number")
        return

    cur.execute("SELECT * FROM rooms WHERE number=%s", (room_no,))
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO rooms VALUES (%s,%s,%s,'Booked')",
            (room_no, room_type, price)
        )
    else:
        cur.execute(
            "UPDATE rooms SET status='Booked' WHERE number=%s",
            (room_no,) )

    cur.execute(
        "INSERT INTO customers VALUES (%s,%s,%s,%s,%s,NULL)",
        (cid, name, phone, room_no, today) )

    con.commit()
    print("Customer added successfully")

def display_customers():
    cur.execute("SELECT * FROM customers")
    rows = cur.fetchall()

    for r in rows:
        print(r)
        
def delete_customer():
    cid = int(input("Customer ID: "))
    
    cur.execute("SELECT number FROM customers WHERE cid=%s", (cid,))
    result = cur.fetchone()
    if result is None:
        print("Customer not found")
        return
    room = result[0]

    cur.execute("DELETE FROM customers WHERE cid=%s", (cid,))
    cur.execute("UPDATE rooms SET status='Available' WHERE number=%s", (room,))
    
    con.commit()
    print("Customer checked out")
def add_service():
    cid = int(input("Customer ID: "))
    s = input("Service Name: ")
    cost = int(input("Cost: "))

    cur.execute(
        "INSERT INTO services VALUES (%s,%s,%s)",
        (cid, s, cost)  )

    con.commit()
    print("Service added")
def generate_bill():
    cid = int(input("Customer ID: "))

    cur.execute("""
        SELECT price FROM rooms
        WHERE number = (
            SELECT number FROM customers WHERE cid=%s
        )
    """, (cid,))
    room_price = cur.fetchone()[0]

    cur.execute("SELECT SUM(cost) FROM services WHERE cid=%s", (cid,))
    service_cost = cur.fetchone()[0]

    if service_cost is None:
        service_cost = 0

    total = room_price + service_cost

    print("Room Charges:", room_price)
    print("Service Charges:", service_cost)
    print("Total Bill:", total)
def menu():
    while True:
        print('''
        1. Add Customer 
        2. Display Customers 
        3. Checkout Customer 
        4. Add Services
        5. Generate Bill
        6. Exit
        ''')

        ch = int(input("Enter choice: "))

        if ch == 1:
            add_customer()
        elif ch == 2:
            display_customers()
        elif ch == 3:
            delete_customer()
        elif ch == 4:
            add_service()
        elif ch == 5:
            generate_bill()
        elif ch == 6:
            break
        else:
            print("Invalid choice")

def start():
    print("1. Admin Login")
    print("2. Continue without login")

    ch = input("Choose: ")

    if ch == "1":
        admin_login()
    else:
        menu()

start()
