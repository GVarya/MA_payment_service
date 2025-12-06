import json
import asyncio
from aio_pika import connect_robust, Message

from app.settings import settings
from app.models.order import Order

async def send_payment_success(order: Order) -> None:
    connection = await connect_robust(settings.amqp_url)
    channel = await connection.channel()

    hw_queue = await channel.declare_queue(
        "payment_success_queue",
        durable=True,
    )

    body = json.dumps(
        {
            "payment_id": str(order.id),
            "student_id": str(order.student_id),
            "course_id": str(order.course_id),
        }
    ).encode()

    await channel.default_exchange.publish(
        Message(body=body),
        routing_key=hw_queue.name,
    )

    await connection.close()

async def send_course_access_granted(order: Order) -> None:
    connection = await connect_robust(settings.amqp_url)
    channel = await connection.channel()

    course_queue = await channel.declare_queue(
        "course_access_queue",
        durable=True,
    )

    body = json.dumps(
        {
            "student_id": str(order.student_id),
            "course_id": str(order.course_id),
            "student_name": order.student_name,
            "student_email": order.student_email,
        }
    ).encode()

    await channel.default_exchange.publish(
        Message(body=body),
        routing_key=course_queue.name,
    )

    await connection.close()
