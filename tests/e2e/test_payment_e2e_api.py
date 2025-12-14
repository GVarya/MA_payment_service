import pytest
import requests
from uuid import uuid4

BASE_URL = "http://payment_service:8001/api"

@pytest.fixture(scope="session")
def student_id():
    return str(uuid4())

@pytest.fixture(scope="session")
def course_id():
    return str(uuid4())


def test_get_orders_list():
    resp = requests.get(f"{BASE_URL}/payments/orders")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


def test_create_order(student_id, course_id):
    order_data = {
        "student_id": student_id,
        "student_name": "Test Student",
        "student_email": "test@example.com",
        "course_id": course_id,
        "amount": 15000.0,
    }
    resp = requests.post(f"{BASE_URL}/payments/orders", json=order_data)
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data["student_name"] == order_data["student_name"]
    assert data["amount"] == order_data["amount"]
    assert data["status"].lower() == "created"


def test_get_student_orders(student_id, course_id):
    order_data = {
        "student_id": student_id,
        "student_name": "Ivan Petrov",
        "student_email": "ivan@example.com",
        "course_id": course_id,
        "amount": 20000.0,
    }
    create_resp = requests.post(f"{BASE_URL}/payments/orders", json=order_data)
    assert create_resp.status_code in (200, 201)

    resp = requests.get(f"{BASE_URL}/payments/orders/student/{student_id}")
    assert resp.status_code == 200
    orders = resp.json()
    assert isinstance(orders, list)
    assert any(o["student_name"] == "Ivan Petrov" for o in orders)


def test_initiate_payment(student_id, course_id):
    order_data = {
        "student_id": student_id,
        "student_name": "Petr Smirnov",
        "student_email": "petr@example.com",
        "course_id": course_id,
        "amount": 25000.0,
    }
    create_resp = requests.post(f"{BASE_URL}/payments/orders", json=order_data)
    assert create_resp.status_code in (200, 201)
    order_id = create_resp.json()["id"]

    payment_data = {"order_id": order_id}
    resp = requests.post(f"{BASE_URL}/payments/initiate", json=payment_data)
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data["order_id"] == order_id
    assert data["amount"] == 25000.0
    assert data["status"].lower() == "pending"


def test_confirm_payment(student_id, course_id):
    order_data = {
        "student_id": student_id,
        "student_name": "Anna Smirnova",
        "student_email": "anna@example.com",
        "course_id": course_id,
        "amount": 30000.0,
    }
    create_resp = requests.post(f"{BASE_URL}/payments/orders", json=order_data)
    assert create_resp.status_code in (200, 201)
    order_id = create_resp.json()["id"]

    payment_data = {"order_id": order_id}
    payment_resp = requests.post(f"{BASE_URL}/payments/initiate", json=payment_data)
    assert payment_resp.status_code in (200, 201)
    payment_id = payment_resp.json()["id"]

    confirm_data = {
        "payment_id": payment_id,
        "transaction_id": str(payment_id),
    }
    resp = requests.post(f"{BASE_URL}/payments/confirm", json=confirm_data)
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data["status"].lower() == "success"


def test_payment_workflow_complete(student_id, course_id):
    order_data = {
        "student_id": student_id,
        "student_name": "Complete Flow Student",
        "student_email": "complete@example.com",
        "course_id": course_id,
        "amount": 35000.0,
    }
    order_resp = requests.post(f"{BASE_URL}/payments/orders", json=order_data)
    assert order_resp.status_code in (200, 201)
    order = order_resp.json()
    order_id = order["id"]
    assert order["status"].lower() == "created"

    payment_data = {"order_id": order_id}
    payment_resp = requests.post(f"{BASE_URL}/payments/initiate", json=payment_data)
    assert payment_resp.status_code in (200, 201)
    payment = payment_resp.json()
    payment_id = payment["id"]
    assert payment["status"].lower() == "pending"
    assert payment["amount"] == 35000.0

    confirm_data = {
        "payment_id": payment_id,
        "transaction_id": str(payment_id),
    }
    confirm_resp = requests.post(f"{BASE_URL}/payments/confirm", json=confirm_data)
    assert confirm_resp.status_code in (200, 201)
    confirmed = confirm_resp.json()
    assert confirmed["status"].lower() == "success"

    status_resp = requests.get(f"{BASE_URL}/payments/orders/{order_id}/status")
    assert status_resp.status_code == 200
    status_body = status_resp.json()
    assert status_body["order_id"] == order_id
    assert status_body["status"].lower() in ("created", "paid", "success", "completed", "payment_initiated", "payment_success")


def test_multiple_orders(student_id, course_id):
    order1 = {
        "student_id": student_id,
        "student_name": "Student One",
        "student_email": "one@example.com",
        "course_id": course_id,
        "amount": 10000.0,
    }
    resp1 = requests.post(f"{BASE_URL}/payments/orders", json=order1)
    assert resp1.status_code in (200, 201)

    order2 = {
        "student_id": str(uuid4()),
        "student_name": "Student Two",
        "student_email": "two@example.com",
        "course_id": course_id,
        "amount": 15000.0,
    }
    resp2 = requests.post(f"{BASE_URL}/payments/orders", json=order2)
    assert resp2.status_code in (200, 201)

    list_resp = requests.get(f"{BASE_URL}/payments/orders")
    assert list_resp.status_code == 200
    orders = list_resp.json()
    assert isinstance(orders, list)
    assert len(orders) >= 2
