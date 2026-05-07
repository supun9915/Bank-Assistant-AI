"""
Pydantic models for chat API
"""
from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(
        ..., 
        min_length=1, 
        max_length=500,
        description="User input message"
    )
    user_id: Optional[int] = Field(
        default=1,
        description="User ID for personalized responses"
    )
    last_intent: Optional[str] = Field(
        default=None,
        description="Intent detected from the previous message, used for context-aware follow-up responses"
    )
    account_number: Optional[str] = Field(
        default=None,
        description="Verified account number for personal account queries"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "What is my account balance?",
                "user_id": 1
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    reply: str = Field(
        ..., 
        description="Bot response message"
    )
    intent: Optional[str] = Field(
        None,
        description="Detected intent"
    )
    confidence: Optional[float] = Field(
        None,
        description="Intent detection confidence score"
    )
    data: Optional[dict] = Field(
        None,
        description="Additional data (e.g., balance, transactions)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "reply": "Your account balance is $5,250.00",
                "intent": "BALANCE",
                "confidence": 0.95,
                "data": {"balance": 5250.00}
            }
        }
