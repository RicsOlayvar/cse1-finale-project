import pytest
import requests

BASE_URL = "http://127.0.0.1:5000"

# --- Home Test ---
def test_home():
    r = requests.get(BASE_URL + "/")
    assert r.status_code == 200
    assert "Salon API" in r.text

# --- Customers Tests ---
def test_add_customer():
    payload = {
        "CustomerID": 23,
        "CustomerName": "Test23 User",
        "Phone": "09990000000",
        "Email": "test@example.com"
    }
    r = requests.post(BASE_URL + "/customers", json=payload)
    assert r.status_code in [201, 400]   # 201 kung bagong record, 400 kung duplicate

def test_get_customers():
    r = requests.get(BASE_URL + "/customers")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_update_customer():
    payload = {
        "CustomerName": "Anna Updated",
        "Phone": "09170000000",
        "Email": "anna.updated@gmail.com"
    }
    r = requests.put(BASE_URL + "/customers/1", json=payload)  # existing si Anna Cruz
    assert r.status_code in [200, 404]

def test_delete_customer():
    r = requests.delete(BASE_URL + "/customers/99")  # gamitin yung test customer na walang dependencies
    assert r.status_code in [200, 404]

# --- Schedules Tests ---
def test_add_schedule():
    payload = {
        "ScheduleID": 90,
        "CustomerID": 23,
        "ServiceType": "Test Service",
        "AppointmentDate": "2025-12-30",
        "AppointmentTime": "10:00",
        "Duration": "60",
        "Status": "Booked"
    }
    r = requests.post(BASE_URL + "/schedules", json=payload)
    assert r.status_code in [201, 400]

def test_get_schedules():
    r = requests.get(BASE_URL + "/schedules")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_update_schedule():
    payload = {
        "CustomerID": 1,
        "ServiceType": "Hair Coloring",
        "AppointmentDate": "2025-12-14",
        "AppointmentTime": "15:00",
        "Duration": "120",
        "Status": "Confirmed"
    }
    r = requests.put(BASE_URL + "/schedules/1", json=payload)  # existing schedule kay Anna
    assert r.status_code in [200, 404]

def test_delete_schedule():
    r = requests.delete(BASE_URL + "/schedules/99")  # gamitin yung test schedule na walang dependencies
    assert r.status_code in [200, 404]

# --- Payments Tests ---
def test_add_payment():
    payload = {
        "PaymentID": 23,
        "ScheduleID": 2,
        "Amount": 999,
        "PaymentDate": "2025-12-31",
        "Method": "Cash",
        "Status": "Paid"
    }
    r = requests.post(BASE_URL + "/payments", json=payload)
    assert r.status_code in [201, 400]

def test_get_payments():
    r = requests.get(BASE_URL + "/payments")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_update_payment():
    payload = {
        "ScheduleID": 1,
        "Amount": 1000,
        "PaymentDate": "2025-12-31",
        "Method": "Card",
        "Status": "Confirmed"
    }
    r = requests.put(BASE_URL + "/payments/1", json=payload)  # existing payment ID=1
    assert r.status_code in [200, 404]

def test_delete_payment():
    r = requests.delete(BASE_URL + "/payments/99")  # gamitin yung test payment na walang dependencies
    assert r.status_code in [200, 404]

# --- End of Tests ---
