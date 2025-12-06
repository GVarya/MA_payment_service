from fastapi import FastAPI
from app.endpoints.payment_router import router as payment_router

app = FastAPI(title="Payment Service")
app.include_router(payment_router, prefix="/api")
