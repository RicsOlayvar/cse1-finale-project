# Salon Services API

A secure RESTful API for managing customers, schedules, and payments in a salon system.  
This project is part of **CSE1 Finale Project** using Flask + MySQL with JWT authentication.

---

## ✨ Features
- 🔐 **JWT Authentication** (Login + Refresh tokens)
- 👥 **Customers CRUD** (Create, Read, Update, Delete, Search)
- 📅 **Schedules CRUD** (linked to Customers)
- 💳 **Payments CRUD** (linked to Schedules)
- 🔎 **Search endpoints**
- 📄 **XML/JSON output support**
- ✅ **Error handling** (`400 Bad Request`, `404 Not Found`)

---

## ⚙️ Installation

```bash
# Clone repository
git clone https://github.com/yourusername/cse1-finale-project.git
cd cse1-finale-project

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

#Configuration 
Update app.py with your MySQL credentials:
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'salon_services'

#Running the app
python app.py
API will run at: http://127.0.0.1:5000

🔐 Authentication
Login with:

json
{
  "username": "admin",
  "password": "1234"
}

Response:

json
{
  "access_token": "...",
  "refresh_token": "..."
}
Use header:

Code
Authorization: Bearer <access_token>

Endpoints
Auth
POST /login → Get JWT token

POST /refresh → Refresh token

Customers
POST /customers → Add customer

GET /customers → List customers (JSON/XML)

PUT /customers/<id> → Update customer

DELETE /customers/<id> → Delete customer

GET /customers/search?q=<keyword> → Search customers

Schedules
POST /schedules → Add schedule

GET /schedules → List schedules (with customer info)

PUT /schedules/<id> → Update schedule

DELETE /schedules/<id> → Delete schedule

Payments
POST /payments → Add payment

GET /payments → List payments

PUT /payments/<id> → Update payment

DELETE /payments/<id> → Delete payment

⚠️ Error Handling
400 Bad Request → Missing fields, invalid input, foreign key errors

404 Not Found → Record does not exist

500 Internal Server Error → Avoided with try/except

🧪 Testing
Run unit tests with pytest:
bash
pytest -v
Covers:

Home route
Customers CRUD
Schedules CRUD
Payments CRUD

Auth (login, refresh)


💻 Sample curl Commands
bash
# Login
curl -X POST http://127.0.0.1:5000/login \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"1234"}'

# Get customers
curl -X GET http://127.0.0.1:5000/customers \
     -H "Authorization: Bearer <token>"

## 📦 Requirements

The project uses the following dependencies (see `requirements.txt`):

- **Flask** – main web framework for building the API  
- **Flask-MySQLdb** + **mysqlclient** – connect and interact with MySQL database (`salon_services`)  
- **Flask-JWT-Extended / PyJWT** – handle JWT authentication (login, refresh tokens)  
- **xmltodict** – convert JSON responses into XML format  
- **pytest** – run unit tests for endpoints  
- **requests** – send HTTP requests in tests  
- **Flask-Bcrypt** – optional password hashing support  
- **Werkzeug, Jinja2, itsdangerous, MarkupSafe, click, colorama, blinker, importlib-metadata** – supporting libraries required by Flask and testing environment

🛠 How to Use
Make sure that the requirements.txt file is located in the root folder of your repository (cse1-finale-project).

When setting up a new environment, simply run:

bash
pip install -r requirements.txt
This will automatically install all the required packages in the correct versions.