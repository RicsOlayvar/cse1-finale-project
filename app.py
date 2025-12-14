from flask import Flask, request, jsonify, make_response
from flask_mysqldb import MySQL
import xmltodict
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token,jwt_required, get_jwt_identity

app = Flask(__name__)

# --- Database config ---
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'salon_services'

# --- JWT config ---
app.config["JWT_SECRET_KEY"] = "super-secret-key"  
jwt = JWTManager(app)

mysql = MySQL(app)

#output formatting ---
def format_output(data, fmt, wrapper_name="item"):
    if fmt == "xml":
        # Wrap data in a named container (e.g., customers, schedules)
        xml_data = { "response": { wrapper_name: data } }
        xml_str = xmltodict.unparse(xml_data, pretty=True, indent="  ")
        return make_response(xml_str, 200, {"Content-Type": "application/xml"})
    # default JSON
    return make_response(jsonify(data), 200)


# --- Home route ---
@app.route('/')
def home():
    return "Salon API is running!"

# --- JWT Login ---
@app.route("/login", methods=["POST"])
def login():
    # Try JSON first
    if request.is_json:
        username = request.json.get("username")
        password = request.json.get("password")
    else:
        # Fallback to form data (HTML form submission)
        username = request.form.get("username")
        password = request.form.get("password")

    if username == "admin" and password == "1234":
        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)
        return jsonify(access_token=access_token, refresh_token=refresh_token), 200
    return jsonify(msg="Bad credentials"), 401

# --- JWT Login Page (GET) ---
@app.route("/login", methods=["GET"])
def login_page():
    return """
    <h2>Salon API Login</h2>
    <form method="post" action="/login">
        <label>Username:</label><br>
        <input type="text" name="username"><br>
        <label>Password:</label><br>
        <input type="password" name="password"><br><br>
        <input type="submit" value="Login">
    </form>
    """


# --- Refresh Token ---
@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    new_access_token = create_access_token(identity=identity)
    return jsonify(access_token=new_access_token), 200

# --- Customers CRUD ---
@app.route('/customers', methods=['POST'])
@jwt_required()
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
        return jsonify({"error": str(e)}), 400

@app.route('/customers', methods=['GET'])
@jwt_required()
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
@jwt_required()
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
@jwt_required()
def delete_customer(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Customers WHERE CustomerID=%s", (id,))
    mysql.connection.commit()
    if cur.rowcount == 0:
        return jsonify({"error": "Customer not found"}), 404
    cur.close()
    return jsonify({"message": "Customer deleted"})

# --- Search Customers ---
@app.route('/customers/search', methods=['GET'])
@jwt_required()
def search_customers():
    keyword = request.args.get("q")
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Customers WHERE CustomerName LIKE %s", (f"%{keyword}%",))
    rows = cur.fetchall()
    cur.close()
    result = [{"CustomerID": r[0], "CustomerName": r[1], "Phone": r[2], "Email": r[3]} for r in rows]
    return format_output(result, request.args.get("format"))

# --- Schedules CRUD (protected with JWT) ---
@app.route('/schedules', methods=['POST'])
@jwt_required()
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
@jwt_required()
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

# --- Payments CRUD (protected with JWT) ---
@app.route('/payments', methods=['POST'])
@jwt_required()
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
@jwt_required()
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





# --- Run app ---
if __name__ == '__main__':
    app.run(port=5000, debug=True)
