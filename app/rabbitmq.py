import asyncio
import json
import logging
import traceback

from aio_pika import connect_robust, IncomingMessage
from app.settings import settings

logger = logging.getLogger(__name__)

async def process_payment_event(msg: IncomingMessage):
    """Обработка событий платежа"""
    try:
        data = json.loads(msg.body.decode())
        logger.info(f"Processing payment event: {data}")
        await msg.ack()
    except Exception as e:
        logger.error(f"Error processing payment event: {e}")
        traceback.print_exc()
        await msg.ack()


async def send_payment_success(order):
    """Отправить сообщение о успешном платеже в homework_service"""
    try:
        connection = await connect_robust(settings.amqp_url, timeout=10)
        async with connection:
            channel = await connection.channel()
            exchange = await channel.declare_exchange('payments', auto_delete=False)
            
            message_body = json.dumps({
                "course_id": str(order.course_id),
                "student_id": str(order.student_id),
                "student_name": order.student_name,
                "student_email": order.student_email,
            }).encode()
            
            from aio_pika import Message
            message = Message(message_body, delivery_mode=1)
            
            await exchange.publish(message, routing_key='homework.activate')
            logger.info(f"Sent payment success message for order {order.id}")
    except Exception as e:
        logger.error(f"Failed to send payment success message: {e}")


async def send_course_access_granted(order):
    """Отправить сообщение о предоставлении доступа к курсу"""
    try:
        connection = await connect_robust(settings.amqp_url, timeout=10)
        async with connection:
            channel = await connection.channel()
            exchange = await channel.declare_exchange('course_access', auto_delete=False)
            
            message_body = json.dumps({
                "course_id": str(order.course_id),
                "student_id": str(order.student_id),
                "access_level": "full",
            }).encode()
            
            from aio_pika import Message
            message = Message(message_body, delivery_mode=1)
            
            await exchange.publish(message, routing_key='course.access_granted')
            logger.info(f"Sent course access granted message for student {order.student_id}")
    except Exception as e:
        logger.error(f"Failed to send course access message: {e}")


async def consume():
    """Подключится к RabbitMQ и слушать сообщения"""
    max_retries = 10
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to connect to RabbitMQ (attempt {attempt + 1}/{max_retries})...")
            
            connection = await connect_robust(settings.amqp_url, timeout=10)
            async with connection:
                channel = await connection.channel()
                logger.info("✅ Successfully connected to RabbitMQ (Payment Service)")
                
                # Просто слушаем бесконечно
                # Если нужно слушать очередь:
                # queue = await channel.declare_queue('payment_events')
                # async with queue.iterator() as queue_iter:
                #     async for message in queue_iter:
                #         await process_payment_event(message)
                
                await asyncio.sleep(999999)
                
        except Exception as e:
            logger.error(f"❌ RabbitMQ connection error: {e}")
            
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error("Max retries reached. RabbitMQ consumer will not start.")
                break