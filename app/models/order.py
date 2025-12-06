import enum
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class OrderStatus(str, enum.Enum):
    CREATED = "created"
    PAYMENT_INITIATED = "payment_initiated"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    COURSE_ACCESS_GRANTED = "course_access_granted"

class Order(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    student_id: UUID
    student_name: str
    student_email: str
    course_id: UUID
    amount: float
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
