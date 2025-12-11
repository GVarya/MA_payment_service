# tests/unit/test_payment_service.py

import pytest
from uuid import uuid4

from app.services.payment_service import PaymentService
from app.models.order import OrderStatus
from app.models.payment import PaymentStatus
from app.models.requests import CreateOrderRequest, InitiatePaymentRequest, ConfirmPaymentRequest


@pytest.fixture(scope='session')
def payment_service():
    """Фикстура с сервисом платежей"""
    return PaymentService()


@pytest.fixture(scope='session')
def student_id():
    return uuid4()


@pytest.fixture(scope='session')
def course_id():
    return uuid4()


def test_create_order(payment_service: PaymentService, student_id, course_id):
    """Тест создания заказа"""
    request = CreateOrderRequest(
        student_id=student_id,
        student_name='Ivan Ivanov',
        student_email='ivan@example.com',
        course_id=course_id,
        amount=10000.0
    )
    order = payment_service.create_order(request)
    
    assert order.student_name == 'Ivan Ivanov'
    assert order.amount == 10000.0
    assert order.status == OrderStatus.CREATED


def test_initiate_payment(payment_service: PaymentService, student_id, course_id):
    """Тест инициации платежа"""
    # Создаём заказ
    create_req = CreateOrderRequest(
        student_id=student_id,
        student_name='Petr Petrov',
        student_email='petr@example.com',
        course_id=course_id,
        amount=15000.0
    )
    order = payment_service.create_order(create_req)
    
    # Инициируем платёж
    initiate_req = InitiatePaymentRequest(order_id=order.id)
    payment = payment_service.initiate_payment(initiate_req)
    
    assert payment.order_id == order.id
    assert payment.amount == 15000.0
    assert payment.status == PaymentStatus.PENDING


def test_initiate_payment_wrong_status(payment_service: PaymentService, student_id, course_id):
    """Тест ошибки при инициации платежа для уже обработанного заказа"""
    create_req = CreateOrderRequest(
        student_id=student_id,
        student_name='Test User',
        student_email='test@example.com',
        course_id=course_id,
        amount=5000.0
    )
    order = payment_service.create_order(create_req)
    
    # Инициируем первый раз
    initiate_req = InitiatePaymentRequest(order_id=order.id)
    payment_service.initiate_payment(initiate_req)
    
    # Пробуем инициировать второй раз
    with pytest.raises(ValueError):
        payment_service.initiate_payment(initiate_req)


def test_confirm_payment(payment_service: PaymentService, student_id, course_id):
    """Тест подтверждения платежа"""
    # Создаём заказ
    create_req = CreateOrderRequest(
        student_id=student_id,
        student_name='Anna Sidorova',
        student_email='anna@example.com',
        course_id=course_id,
        amount=20000.0
    )
    order = payment_service.create_order(create_req)
    
    # Инициируем платёж
    initiate_req = InitiatePaymentRequest(order_id=order.id)
    payment = payment_service.initiate_payment(initiate_req)
    
    # Подтверждаем платёж
    confirm_req = ConfirmPaymentRequest(
        payment_id=payment.id,
        transaction_id=str(payment.id)
    )
    confirmed_payment = payment_service.confirm_payment(confirm_req)
    
    assert confirmed_payment.status == PaymentStatus.SUCCESS


def test_confirm_payment_wrong_status(payment_service: PaymentService, student_id, course_id):
    """Тест ошибки при повторном подтверждении платежа"""
    create_req = CreateOrderRequest(
        student_id=student_id,
        student_name='Test',
        student_email='test@example.com',
        course_id=course_id,
        amount=8000.0
    )
    order = payment_service.create_order(create_req)
    
    initiate_req = InitiatePaymentRequest(order_id=order.id)
    payment = payment_service.initiate_payment(initiate_req)
    
    # Подтверждаем первый раз
    confirm_req = ConfirmPaymentRequest(
        payment_id=payment.id,
        transaction_id=str(payment.id)
    )
    payment_service.confirm_payment(confirm_req)
    
    # Пробуем подтвердить второй раз
    with pytest.raises(ValueError):
        payment_service.confirm_payment(confirm_req)