"""
Chat API Routes
"""
import logging
from fastapi import APIRouter, HTTPException, status
from models.chat_models import ChatRequest, ChatResponse
from services.chat_service import process_chat_message

logger = logging.getLogger(__name__)

# Create router for chat endpoints
router = APIRouter()


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint - Processes user messages and returns bot responses
    
    Args:
        request: ChatRequest with user message and optional user_id
        
    Returns:
        ChatResponse with bot reply and metadata
        
    Raises:
        HTTPException: If processing fails
    """
    try:
        logger.info(f"Received chat request: {request.message[:50]}...")
        
        # Validate input
        if not request.message or not request.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )
        
        # Process the message
        response_data = process_chat_message(
            message=request.message.strip(),
            user_id=request.user_id
        )
        
        # Create response model
        response = ChatResponse(
            reply=response_data.get('reply', 'Sorry, I could not process your request.'),
            intent=response_data.get('intent'),
            confidence=response_data.get('confidence'),
            data=response_data.get('data')
        )
        
        logger.info(f"Chat response generated successfully for intent: {response.intent}")
        return response
        
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error processing your request"
        )


@router.get("/chat/health")
async def chat_health():
    """Health check for chat service"""
    return {
        "status": "healthy",
        "service": "chat",
        "message": "Chat service is operational"
    }
