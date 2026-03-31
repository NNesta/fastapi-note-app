from fastapi import APIRouter, Depends, status
from service import Payment, payment
from typing import Annotated


router = APIRouter()

@router.post("/", response_model=str, status_code=status.HTTP_201_CREATED)
async def checkout():
    return payment.pay()
