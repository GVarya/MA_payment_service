from uuid import UUID
from datetime import datetime
from app.models.order import Order, OrderStatus

orders: list[Order] = []

class OrderRepo:
    def get_orders(self) -> list[Order]:
        return orders

    def get_order_by_id(self, id: UUID) -> Order:
        for o in orders:
            if o.id == id:
                return o
        raise KeyError

    def create_order(self, order: Order) -> Order:
        if any(o.id == order.id for o in orders):
            raise KeyError("Order already exists")
        orders.append(order)
        return order

    def set_status(self, id: UUID, status: OrderStatus) -> Order:
        for o in orders:
            if o.id == id:
                o.status = status
                o.updated_at = datetime.utcnow()
                break
        return self.get_order_by_id(id)

    def get_order_by_student(self, student_id: UUID) -> list[Order]:
        return [o for o in orders if o.student_id == student_id]
