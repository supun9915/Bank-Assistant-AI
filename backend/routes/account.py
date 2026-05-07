"""
Account verification routes — OTP send / verify
"""
import random
import logging
import time
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from services.email_service import send_otp_email
from db import get_user_by_email_and_account, save_verified_user

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory OTP store: { email -> {otp, expiry, id_number, account_number} }
_otp_store: dict = {}

OTP_EXPIRY_SECONDS = 300  # 5 minutes


class SendOtpRequest(BaseModel):
    email: str
    id_number: str
    account_number: str


class VerifyOtpRequest(BaseModel):
    email: str
    otp: str


class SendOtpResponse(BaseModel):
    success: bool
    message: str


class VerifyOtpResponse(BaseModel):
    success: bool
    message: str
    account_holder: Optional[str] = None
    account_number: Optional[str] = None
    account_type: Optional[str] = None
    user_id: Optional[int] = None


def _generate_otp() -> str:
    return str(random.randint(100000, 999999))


@router.post("/account/send-otp", response_model=SendOtpResponse)
async def send_otp(request: SendOtpRequest):
    """
    Validate email + account_number against the DB, then send a 6-digit OTP.
    """
    email = request.email.strip().lower()
    account_number = request.account_number.strip()
    id_number = request.id_number.strip()

    # Validate the email + id_number + account_number combination exists in DB
    account_info = get_user_by_email_and_account(email, id_number, account_number)
    if not account_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with the provided email and account number. Please check your details."
        )

    # Generate and store OTP
    otp = _generate_otp()
    _otp_store[email] = {
        "otp": otp,
        "expiry": time.time() + OTP_EXPIRY_SECONDS,
        "id_number": id_number,
        "account_number": account_number,
        "user_id": account_info["user_id"],
        "account_holder": account_info["account_holder"],
        "account_type": account_info["account_type"],
    }

    sent = send_otp_email(
        recipient_email=email,
        otp=otp,
        account_holder_name=account_info["account_holder"],
    )

    if not sent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP email. Please try again shortly."
        )

    logger.info(f"OTP sent to {email}")
    return SendOtpResponse(success=True, message=f"OTP sent to {email}. It expires in 5 minutes.")


@router.post("/account/verify-otp", response_model=VerifyOtpResponse)
async def verify_otp(request: VerifyOtpRequest):
    """
    Verify OTP, save user email + id_number to DB, return account info.
    """
    email = request.email.strip().lower()
    provided_otp = request.otp.strip()

    entry = _otp_store.get(email)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No OTP was requested for this email. Please request a new OTP."
        )

    if time.time() > entry["expiry"]:
        del _otp_store[email]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired. Please request a new one."
        )

    if provided_otp != entry["otp"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP. Please check the code sent to your email."
        )

    # Save email + id_number to verified_users table
    save_verified_user(email=email, id_number=entry["id_number"])

    # Clean up OTP
    del _otp_store[email]

    logger.info(f"Account verified for {email}")
    return VerifyOtpResponse(
        success=True,
        message="Identity verified successfully.",
        account_holder=entry["account_holder"],
        account_number=entry["account_number"],
        account_type=entry["account_type"],
        user_id=entry["user_id"],
    )
