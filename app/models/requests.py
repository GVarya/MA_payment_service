from uuid import UUID
from pydantic import BaseModel, EmailStr

class CreateOrderRequest(BaseModel):
    student_id: UUID
    student_name: str
    student_email: str
    course_id: UUID
    amount: float

class InitiatePaymentRequest(BaseModel):
    order_id: UUID

class ConfirmPaymentRequest(BaseModel):
    payment_id: UUID
    transaction_id: str 