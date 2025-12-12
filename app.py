from flask import Flask, request, jsonify
from flask_mysqldb import MySQL 

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
    # JOIN para makuha ang schedule at customer info
    cur.execute("""
        SELECT s.ScheduleID, s.ServiceType, s.AppointmentDate, s.AppointmentTime,
               s.Duration, s.Status,
               c.CustomerID, c.CustomerName, c.Phone, c.Email
        FROM Schedules s
        JOIN Customers c ON s.CustomerID = c.CustomerID
    """)
    rows = cur.fetchall()
    cur.close()
    return jsonify(rows)


# --- Run app (isa lang dapat) ---
if __name__ == '__main__':
    app.run(debug=True)
