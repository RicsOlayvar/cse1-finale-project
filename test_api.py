import pytest
import requests

BASE_URL = "http://127.0.0.1:5000"

@pytest.fixture(scope="session")
def token():
    payload = {"username": "admin", "password": "1234"}
    r = requests.post(BASE_URL + "/login", json=payload)
    assert r.status_code == 200
    return r.json()["access_token"]

def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}

# --- Home Test ---
def test_home():
    r = requests.get(BASE_URL + "/")
    assert r.status_code == 200
    assert "Salon API" in r.text

# --- Customers Tests ---
def test_add_customer(token):
    payload = {
        "CustomerID": 23,
        "CustomerName": "Test23 User",
        "Phone": "09990000000",
        "Email": "test@example.com"
    }
    r = requests.post(BASE_URL + "/customers", json=payload, headers=auth_headers(token))
    assert r.status_code in [201, 400]

def test_get_customers(token):
    r = requests.get(BASE_URL + "/customers", headers=auth_headers(token))
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_update_customer(token):
    payload = {
        "CustomerName": "Anna Updated",
        "Phone": "09170000000",
        "Email": "anna.updated@gmail.com"
    }
    r = requests.put(BASE_URL + "/customers/1", json=payload, headers=auth_headers(token))
    assert r.status_code in [200, 404]

def test_delete_customer(token):
    r = requests.delete(BASE_URL + "/customers/99", headers=auth_headers(token))
    assert r.status_code in [200, 404]

# --- Schedules Tests ---
def test_add_schedule(token):
    payload = {
        "ScheduleID": 90,
        "CustomerID": 23,
        "ServiceType": "Test Service",
        "AppointmentDate": "2025-12-30",
        "AppointmentTime": "10:00",
        "Duration": "60",
        "Status": "Booked"
    }
    r = requests.post(BASE_URL + "/schedules", json=payload, headers=auth_headers(token))
    assert r.status_code in [201, 400]

def test_get_schedules(token):
    r = requests.get(BASE_URL + "/schedules", headers=auth_headers(token))
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_update_schedule(token):
    payload = {
        "CustomerID": 1,
        "ServiceType": "Hair Coloring",
        "AppointmentDate": "2025-12-14",
        "AppointmentTime": "15:00",
        "Duration": "120",
        "Status": "Confirmed"
    }
    r = requests.put(BASE_URL + "/schedules/1", json=payload, headers=auth_headers(token))
    assert r.status_code in [200, 404]

def test_delete_schedule(token):
    r = requests.delete(BASE_URL + "/schedules/99", headers=auth_headers(token))
    assert r.status_code in [200, 404]

# --- Payments Tests ---
def test_add_payment(token):
    payload = {
        "PaymentID": 23,
        "ScheduleID": 2,
        "Amount": 999,
        "PaymentDate": "2025-12-31",
        "Method": "Cash",
        "Status": "Paid"
    }
    r = requests.post(BASE_URL + "/payments", json=payload, headers=auth_headers(token))
    assert r.status_code in [201, 400]

def test_get_payments(token):
    r = requests.get(BASE_URL + "/payments", headers=auth_headers(token))
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_update_payment(token):
    payload = {
        "ScheduleID": 1,
        "Amount": 1000,
        "PaymentDate": "2025-12-31",
        "Method": "Card",
        "Status": "Confirmed"
    }
    r = requests.put(BASE_URL + "/payments/1", json=payload, headers=auth_headers(token))
    assert r.status_code in [200, 404]

def test_delete_payment(token):
    r = requests.delete(BASE_URL + "/payments/99", headers=auth_headers(token))
    assert r.status_code in [200, 404]
