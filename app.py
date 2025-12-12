from flask import Flask, request, jsonify
from flask_mysqldb import MySQL 
import MySQLdb.cursors
from decimal import Decimal
from datetime import date, time, datetime

app = Flask(__name__)

# --- Database config muna ---
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'salon_services'

mysql = MySQL(app)

# --- Routes ---
@app.route('/')
def home():
    return "Salon API is running!"

@app.route('/customers', methods=['POST'])
def add_customer():
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO Customers (CustomerID, CustomerName, Phone, Email) VALUES (%s,%s,%s,%s)",
                (data['CustomerID'], data['CustomerName'], data['Phone'], data['Email']))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Customer added"})

@app.route('/customers', methods=['GET'])
def get_customers():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Customers")
    rows = cur.fetchall()
    cur.close()
    return jsonify(rows)

@app.route('/schedules', methods=['GET'])
def get_schedules():
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT s.ScheduleID, s.ServiceType, s.AppointmentDate, s.AppointmentTime,
               s.Duration, s.Status,
               c.CustomerID, c.CustomerName, c.Phone, c.Email
        FROM Schedules s
        JOIN Customers c ON s.CustomerID = c.CustomerID
    """)
    rows = cur.fetchall()
    cur.close()

    # Convert tuples to dict
    result = []
    for r in rows:
        result.append({
            "ScheduleID": r[0],
            "ServiceType": r[1],
            "AppointmentDate": str(r[2]),
            "AppointmentTime": str(r[3]),
            "Duration": r[4],
            "Status": r[5],
            "CustomerID": r[6],
            "CustomerName": r[7],
            "Phone": r[8],
            "Email": r[9]
        })
    return jsonify(result)

def serialize_row(row: dict):
    safe = {}
    for k, v in row.items():
        if isinstance(v, Decimal):
            safe[k] = float(v)              # convert Decimal to float
        elif isinstance(v, (date, time, datetime)):
            safe[k] = v.isoformat()         # convert date/time to string
        else:
            safe[k] = v
    return safe

@app.route('/payments', methods=['GET'])
def get_payments():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        SELECT p.PaymentID, p.Amount, p.PaymentDate, p.Method, p.Status,
               s.ScheduleID, s.ServiceType, s.AppointmentDate, s.AppointmentTime,
               c.CustomerID, c.CustomerName, c.Phone, c.Email
        FROM Payments p
        JOIN Schedules s ON p.ScheduleID = s.ScheduleID
        JOIN Customers c ON s.CustomerID = c.CustomerID
    """)
    rows = cur.fetchall()
    cur.close()

    # convert each row to JSON-safe dict
    result = [serialize_row(r) for r in rows]
    return jsonify(result)

    # serialize each row to JSON-safe types
    safe = [serialize_row(r) for r in rows]
    return jsonify(safe)


# --- Run app (isa lang dapat) ---
if __name__ == '__main__':
    app.run(debug=True)
