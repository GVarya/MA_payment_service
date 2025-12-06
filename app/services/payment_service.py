# from uuid import UUID, uuid4
# from datetime import datetime
# import asyncio

# from app.models.order import Order, OrderStatus
# from app.models.payment import Payment, PaymentStatus
# from app.models.requests import (
#     CreateOrderRequest,
#     InitiatePaymentRequest,
#     ConfirmPaymentRequest,
# )
# from app.repos.local_order_repo import OrderRepo
# from app.repos.local_payment_repo import PaymentRepo
# from app.rabbitmq import send_payment_success, send_course_access_granted

# class PaymentService:
#     def __init__(self) -> None:
#         self.order_repo = OrderRepo()
#         self.payment_repo = PaymentRepo()

#     def create_order(self, dto: CreateOrderRequest) -> Order:

#         order = Order(
#             id=uuid4(),
#             student_id=dto.student_id,
#             student_name=dto.student_name,
#             student_email=dto.student_email,
#             course_id=dto.course_id,
#             amount=dto.amount,
#             status=OrderStatus.CREATED,
#             created_at=datetime.utcnow(),
#             updated_at=datetime.utcnow(),
#         )
#         return self.order_repo.create_order(order)

#     def initiate_payment(self, dto: InitiatePaymentRequest) -> Payment:

#         order = self.order_repo.get_order_by_id(dto.order_id)
        
#         if order.status != OrderStatus.CREATED:
#             raise ValueError("Order not in CREATED status")

#         self.order_repo.set_status(dto.order_id, OrderStatus.PAYMENT_INITIATED)

#         payment = Payment(
#             id=uuid4(),
#             order_id=dto.order_id,
#             amount=order.amount,
#             status=PaymentStatus.PENDING,
#             created_at=datetime.utcnow(),
#             updated_at=datetime.utcnow(),
#         )
#         return self.payment_repo.create_payment(payment)

#     def confirm_payment(self, dto: ConfirmPaymentRequest) -> Payment:

#         payment = self.payment_repo.get_payment_by_id(dto.payment_id)

#         if payment.status != PaymentStatus.PENDING:
#             raise ValueError("Payment not in PENDING status")

#         self.payment_repo.set_status(dto.payment_id, PaymentStatus.SUCCESS)

#         order = self.order_repo.get_order_by_id(payment.order_id)
#         self.order_repo.set_status(payment.order_id, OrderStatus.PAYMENT_SUCCESS)

#         asyncio.create_task(send_payment_success(order))
        
#         asyncio.create_task(send_course_access_granted(order))

#         return payment

#     def get_order_status(self, order_id: UUID) -> OrderStatus:
#         order = self.order_repo.get_order_by_id(order_id)
#         return order.status

#     def get_orders(self) -> list[Order]:
#         return self.order_repo.get_orders()

#     def get_payments(self) -> list[Payment]:
#         return self.payment_repo.get_payments()

#     def get_student_orders(self, student_id: UUID) -> list[Order]:
#         return self.order_repo.get_order_by_student(student_id)


from uuid import UUID, uuid4
from datetime import datetime
import asyncio

from app.models.order import Order, OrderStatus
from app.models.payment import Payment, PaymentStatus
from app.models.requests import (
    CreateOrderRequest,
    InitiatePaymentRequest,
    ConfirmPaymentRequest,
)
from app.repos.local_order_repo import OrderRepo
from app.repos.local_payment_repo import PaymentRepo
from app.rabbitmq import send_payment_success, send_course_access_granted


class PaymentService:
    def __init__(self) -> None:
        self.order_repo = OrderRepo()
        self.payment_repo = PaymentRepo()

    def create_order(self, dto: CreateOrderRequest) -> Order:
        order = Order(
            id=uuid4(),
            student_id=dto.student_id,
            student_name=dto.student_name,
            student_email=dto.student_email,
            course_id=dto.course_id,
            amount=dto.amount,
            status=OrderStatus.CREATED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        return self.order_repo.create_order(order)

    def initiate_payment(self, dto: InitiatePaymentRequest) -> Payment:
        order = self.order_repo.get_order_by_id(dto.order_id)
        
        if order.status != OrderStatus.CREATED:
            raise ValueError("Order not in CREATED status")

        self.order_repo.set_status(dto.order_id, OrderStatus.PAYMENT_INITIATED)

        payment = Payment(
            id=uuid4(),
            order_id=dto.order_id,
            amount=order.amount,
            status=PaymentStatus.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        return self.payment_repo.create_payment(payment)

    def confirm_payment(self, dto: ConfirmPaymentRequest) -> Payment:
        payment = self.payment_repo.get_payment_by_id(dto.payment_id)

        if payment.status != PaymentStatus.PENDING:
            raise ValueError("Payment not in PENDING status")

        self.payment_repo.set_status(dto.payment_id, PaymentStatus.SUCCESS)

        order = self.order_repo.get_order_by_id(payment.order_id)
        self.order_repo.set_status(payment.order_id, OrderStatus.PAYMENT_SUCCESS)

        try:
            import threading
            
            def send_notifications():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(send_payment_success(order))
                    loop.run_until_complete(send_course_access_granted(order))
                    loop.close()
                except Exception as e:
                    print(f"Error sending notifications: {e}")

            thread = threading.Thread(target=send_notifications)
            thread.daemon = True 
            thread.start()
            
        except Exception as e:
            print(f"Failed to send notifications: {e}")
        return payment

    def get_order_status(self, order_id: UUID) -> OrderStatus:
        order = self.order_repo.get_order_by_id(order_id)
        return order.status

    def get_orders(self) -> list[Order]:
        return self.order_repo.get_orders()

    def get_payments(self) -> list[Payment]:
        return self.payment_repo.get_payments()

    def get_student_orders(self, student_id: UUID) -> list[Order]:
        return self.order_repo.get_order_by_student(student_id)