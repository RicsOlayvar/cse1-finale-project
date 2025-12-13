from flask import Flask, request, jsonify, make_response
from flask_mysqldb import MySQL
import MySQLdb.cursors
import xmltodict

app = Flask(__name__)

# --- Database config ---
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'salon_services'

mysql = MySQL(app)

# --- Helper function for output formatting ---
def format_output(data, fmt):
    if fmt == "xml":
        return make_response(xmltodict.unparse({"response": data}), 200)
    return jsonify(data)

# --- Home route ---
@app.route('/')
def home():
    return "Salon API is running!"

# --- Customers CRUD ---
@app.route('/customers', methods=['POST'])
def add_customer():
    data = request.json
    if not data or not data.get('CustomerID') or not data.get('CustomerName') or not data.get('Phone'):
        return jsonify({"error": "Missing required fields"}), 400
    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO Customers (CustomerID, CustomerName, Phone, Email) VALUES (%s,%s,%s,%s)",
                    (data['CustomerID'], data['CustomerName'], data['Phone'], data.get('Email')))
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": "Customer added"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/customers', methods=['GET'])
def get_customers():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Customers")
    rows = cur.fetchall()
    cur.close()
    result = []
    for r in rows:
        result.append({
            "CustomerID": r[0],
            "CustomerName": r[1],
            "Phone": r[2],
            "Email": r[3]
        })
    return format_output(result, request.args.get("format"))

@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    cur = mysql.connection.cursor()
    cur.execute("UPDATE Customers SET CustomerName=%s, Phone=%s, Email=%s WHERE CustomerID=%s",
                (data.get('CustomerName'), data.get('Phone'), data.get('Email'), id))
    mysql.connection.commit()
    if cur.rowcount == 0:
        return jsonify({"error": "Customer not found"}), 404
    cur.close()
    return jsonify({"message": "Customer updated"})

@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Customers WHERE CustomerID=%s", (id,))
    mysql.connection.commit()
    if cur.rowcount == 0:
        return jsonify({"error": "Customer not found"}), 404
    cur.close()
    return jsonify({"message": "Customer deleted"})

# --- Schedules CRUD ---
@app.route('/schedules', methods=['POST'])
def add_schedule():
    data = request.json
    if not data or not data.get('ScheduleID') or not data.get('CustomerID') or not data.get('ServiceType'):
        return jsonify({"error": "Missing required fields"}), 400
    cur = mysql.connection.cursor()
    cur.execute("""INSERT INTO Schedules (ScheduleID, CustomerID, ServiceType, AppointmentDate, AppointmentTime, Duration, Status)
                   VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (data['ScheduleID'], data['CustomerID'], data['ServiceType'],
                 data.get('AppointmentDate'), data.get('AppointmentTime'),
                 data.get('Duration'), data.get('Status')))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Schedule added"}), 201

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
    return format_output(result, request.args.get("format"))

@app.route('/schedules/<int:id>', methods=['PUT'])
def update_schedule(id):
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    cur = mysql.connection.cursor()
    cur.execute("""UPDATE Schedules 
                   SET CustomerID=%s, ServiceType=%s, AppointmentDate=%s, AppointmentTime=%s, Duration=%s, Status=%s 
                   WHERE ScheduleID=%s""",
                (data.get('CustomerID'), data.get('ServiceType'), data.get('AppointmentDate'),
                 data.get('AppointmentTime'), data.get('Duration'), data.get('Status'), id))
    mysql.connection.commit()
    if cur.rowcount == 0:
        return jsonify({"error": "Schedule not found"}), 404
    cur.close()
    return jsonify({"message": "Schedule updated"})

@app.route('/schedules/<int:id>', methods=['DELETE'])
def delete_schedule(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Schedules WHERE ScheduleID=%s", (id,))
    mysql.connection.commit()
    if cur.rowcount == 0:
        return jsonify({"error": "Schedule not found"}), 404
    cur.close()
    return jsonify({"message": "Schedule deleted"})

# --- Payments CRUD ---
@app.route('/payments', methods=['POST'])
def add_payment():
    data = request.json
    if not data or not data.get('PaymentID') or not data.get('ScheduleID') or not data.get('Amount'):
        return jsonify({"error": "Missing required fields"}), 400
    cur = mysql.connection.cursor()
    cur.execute("""INSERT INTO Payments (PaymentID, ScheduleID, Amount, PaymentDate, Method, Status)
                   VALUES (%s,%s,%s,%s,%s,%s)""",
                (data['PaymentID'], data['ScheduleID'], data['Amount'],
                 data.get('PaymentDate'), data.get('Method'), data.get('Status')))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Payment added"}), 201

@app.route('/payments', methods=['GET'])
def get_payments():
    cur = mysql.connection.cursor()
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
    result = []
    for r in rows:
        result.append({
            "PaymentID": r[0],
            "Amount": float(r[1]) if r[1] is not None else None,
            "PaymentDate": str(r[2]),
            "Method": r[3],
            "Status": r[4],
            "ScheduleID": r[5],
            "ServiceType": r[6],
            "AppointmentDate": str(r[7]),
            "AppointmentTime": str(r[8]),
            "CustomerID": r[9],
            "CustomerName": r[10],
            "Phone": r[11],
            "Email": r[12]
        })
    return format_output(result, request.args.get("format"))

@app.route('/payments/<int:id>', methods=['PUT'])
def update_payment(id):
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    cur = mysql.connection.cursor()
    cur.execute("""UPDATE Payments 
                   SET ScheduleID=%s, Amount=%s, PaymentDate=%s, Method=%s, Status=%s 
                   WHERE PaymentID=%s""",
                (data.get('ScheduleID'), data.get('Amount'), data.get('PaymentDate'),
                 data.get('Method'), data.get('Status'), id))
    mysql.connection.commit()
    if cur.rowcount == 0:
        return jsonify({"error": "Payment not found"}), 404
    cur.close()
    return jsonify({"message": "Payment updated"})

@app.route('/payments/<int:id>', methods=['DELETE'])
def delete_payment(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Payments WHERE PaymentID=%s", (id,))
    mysql.connection.commit()
    if cur.rowcount == 0:
        return jsonify({"error": "Payment not found"}), 404         
    cur.close()
    return jsonify({"message": "Payment deleted"})          



# --- Run app (isa lang dapat) ---
if __name__ == '__main__':
    app.run(port=5000, debug=True)
