import enum
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"

class Payment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_id: UUID
    amount: float
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime
