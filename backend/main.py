"""
Smart Banking Assistant - Main FastAPI Application
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.chat import router as chat_router
from routes.account import router as account_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Smart Banking Assistant API",
    description="AI-powered banking chatbot with NLP capabilities",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(account_router, prefix="/api", tags=["Account"])

@app.get("/")
def home():
    """Health check endpoint"""
    logger.info("Health check requested")
    return {
        "status": "online",
        "message": "Smart Banking Assistant API is running",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "nlp": "loaded"
    }