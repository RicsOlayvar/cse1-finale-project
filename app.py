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

@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("UPDATE Customers SET CustomerName=%s, Phone=%s, Email=%s WHERE CustomerID=%s",
                (data['CustomerName'], data['Phone'], data['Email'], id))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Customer updated"})

@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Customers WHERE CustomerID=%s", (id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Customer deleted"})


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
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            p.PaymentID,
            CAST(p.Amount AS CHAR) AS Amount,                      -- Decimal -> string
            DATE_FORMAT(p.PaymentDate, '%%Y-%%m-%%d') AS PaymentDate, -- Date -> string
            p.Method,
            p.Status,
            s.ScheduleID,
            s.ServiceType,
            DATE_FORMAT(s.AppointmentDate, '%%Y-%%m-%%d') AS AppointmentDate, -- Date -> string
            TIME_FORMAT(s.AppointmentTime, '%%H:%%i:%%s') AS AppointmentTime, -- Time -> string
            c.CustomerID,
            c.CustomerName,
            c.Phone,
            c.Email
        FROM Payments p
        JOIN Schedules s ON p.ScheduleID = s.ScheduleID
        JOIN Customers c ON s.CustomerID = c.CustomerID
    """)
    rows = cur.fetchall()
    cur.close()

    result = []
    for r in rows:
        result.append({
            "PaymentID": r[0],
            "Amount": float(r[1]) if r[1] is not None else None,   # parse string to float
            "PaymentDate": r[2],
            "Method": r[3],
            "Status": r[4],
            "ScheduleID": r[5],
            "ServiceType": r[6],
            "AppointmentDate": r[7],
            "AppointmentTime": r[8],
            "CustomerID": r[9],
            "CustomerName": r[10],
            "Phone": r[11],
            "Email": r[12]
        })
    return jsonify(result)

@app.route('/schedules', methods=['POST'])
def add_schedule():
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""INSERT INTO Schedules (ScheduleID, CustomerID, ServiceType, AppointmentDate, AppointmentTime, Duration, Status)
                   VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (data['ScheduleID'], data['CustomerID'], data['ServiceType'],
                 data['AppointmentDate'], data['AppointmentTime'], data['Duration'], data['Status']))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Schedule added"})

@app.route('/schedules/<int:id>', methods=['PUT'])
def update_schedule(id):
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""UPDATE Schedules 
                   SET CustomerID=%s, ServiceType=%s, AppointmentDate=%s, AppointmentTime=%s, Duration=%s, Status=%s 
                   WHERE ScheduleID=%s""",
                (data['CustomerID'], data['ServiceType'], data['AppointmentDate'],
                 data['AppointmentTime'], data['Duration'], data['Status'], id))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Schedule updated"})

@app.route('/schedules/<int:id>', methods=['DELETE'])
def delete_schedule(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Schedules WHERE ScheduleID=%s", (id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Schedule deleted"})
@app.route('/payments', methods=['POST'])
def add_payment():
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""INSERT INTO Payments (PaymentID, ScheduleID, Amount, PaymentDate, Method, Status)
                   VALUES (%s,%s,%s,%s,%s,%s)""",
                (data['PaymentID'], data['ScheduleID'], data['Amount'],
                 data['PaymentDate'], data['Method'], data['Status']))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Payment added"})

@app.route('/payments/<int:id>', methods=['PUT'])
def update_payment(id):
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""UPDATE Payments 
                   SET ScheduleID=%s, Amount=%s, PaymentDate=%s, Method=%s, Status=%s 
                   WHERE PaymentID=%s""",
                (data['ScheduleID'], data['Amount'], data['PaymentDate'],
                 data['Method'], data['Status'], id))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Payment updated"})

@app.route('/payments/<int:id>', methods=['DELETE'])
def delete_payment(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Payments WHERE PaymentID=%s", (id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Payment deleted"})



# --- Run app (isa lang dapat) ---
if __name__ == '__main__':
    app.run(debug=True)
