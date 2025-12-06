from uuid import UUID
from datetime import datetime
from app.models.payment import Payment, PaymentStatus

payments: list[Payment] = []

class PaymentRepo:
    def get_payments(self) -> list[Payment]:
        return payments

    def get_payment_by_id(self, id: UUID) -> Payment:
        for p in payments:
            if p.id == id:
                return p
        raise KeyError

    def create_payment(self, payment: Payment) -> Payment:
        if any(p.id == payment.id for p in payments):
            raise KeyError("Payment already exists")
        payments.append(payment)
        return payment

    def set_status(self, id: UUID, status: PaymentStatus) -> Payment:
        for p in payments:
            if p.id == id:
                p.status = status
                p.updated_at = datetime.utcnow()
                break
        return self.get_payment_by_id(id)

    def get_payment_by_order(self, order_id: UUID) -> Payment:
        for p in payments:
            if p.order_id == order_id:
                return p
        raise KeyError
