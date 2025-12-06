from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException

from app.services.payment_service import PaymentService
from app.models.order import Order
from app.models.payment import Payment
from app.models.requests import (
    CreateOrderRequest,
    InitiatePaymentRequest,
    ConfirmPaymentRequest,
)

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/orders", response_model=Order)
def create_order(
    dto: CreateOrderRequest,
    svc: PaymentService = Depends(),
):
    try:
        return svc.create_order(dto)
    except KeyError:
        raise HTTPException(400, "Order creation failed")

@router.get("/orders", response_model=list[Order])
def get_orders(svc: PaymentService = Depends()):
    return svc.get_orders()

@router.get("/orders/student/{student_id}", response_model=list[Order])
def get_student_orders(
    student_id: UUID,
    svc: PaymentService = Depends(),
):
    return svc.get_student_orders(student_id)


@router.post("/initiate", response_model=Payment)
def initiate_payment(
    dto: InitiatePaymentRequest,
    svc: PaymentService = Depends(),
):
    try:
        return svc.initiate_payment(dto)
    except KeyError:
        raise HTTPException(404, "Order not found")
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.post("/confirm", response_model=Payment)
def confirm_payment(
    dto: ConfirmPaymentRequest,
    svc: PaymentService = Depends(),
):
    try:
        return svc.confirm_payment(dto)
    except KeyError:
        raise HTTPException(404, "Payment not found")
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.get("/payments", response_model=list[Payment])
def get_payments(svc: PaymentService = Depends()):
    return svc.get_payments()

@router.get("/orders/{order_id}/status")
def get_order_status(
    order_id: UUID,
    svc: PaymentService = Depends(),
):
    try:
        status = svc.get_order_status(order_id)
        return {"order_id": order_id, "status": status}
    except KeyError:
        raise HTTPException(404, "Order not found")
