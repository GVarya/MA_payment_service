import pytest
from uuid import uuid4
from datetime import datetime
from pydantic import ValidationError

from app.models.order import Order, OrderStatus
from app.models.payment import Payment, PaymentStatus


@pytest.fixture()
def sample_order_data():
    return {
        'id': uuid4(),
        'student_id': uuid4(),
        'student_name': 'Test Student',
        'student_email': 'test@example.com',
        'course_id': uuid4(),
        'amount': 5000.0,
        'status': OrderStatus.CREATED,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }


def test_order_creation(sample_order_data):
    order = Order(**sample_order_data)
    assert order.id == sample_order_data['id']
    assert order.student_name == 'Test Student'
    assert order.amount == 5000.0
    assert order.status == OrderStatus.CREATED


def test_order_student_name_required():
    with pytest.raises(ValidationError):
        Order(
            id=uuid4(),
            student_id=uuid4(),
            student_email='test@example.com',
            course_id=uuid4(),
            amount=5000.0,
            status=OrderStatus.CREATED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )


def test_order_amount_required():
    with pytest.raises(ValidationError):
        Order(
            id=uuid4(),
            student_id=uuid4(),
            student_name='Test',
            student_email='test@example.com',
            course_id=uuid4(),
            status=OrderStatus.CREATED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )


def test_payment_creation():
    payment = Payment(
        id=uuid4(),
        order_id=uuid4(),
        amount=3000.0,
        status=PaymentStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    assert payment.status == PaymentStatus.PENDING
    assert payment.amount == 3000.0


def test_payment_order_id_required():
    with pytest.raises(ValidationError):
        Payment(
            id=uuid4(),
            amount=3000.0,
            status=PaymentStatus.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )