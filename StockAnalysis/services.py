from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import os

from agent.Agent_StockAnalysis import StockFundamentalAgent

app = FastAPI(title="Stock Analysis Service", version="1.0.0")
security = HTTPBearer()


# Request Model
class StockAnalysisRequest(BaseModel):
    input_text: str
    
    class Config:
        json_schema_extra = {   
            "example": {
                "input_text": "Analyze AAPL stock fundamentals"
            }
        }

# Response Model
class StockAnalysisResponse(BaseModel):
    status: str
    data: dict

# Dependency untuk verify API key
def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify Groq API key from Authorization header
    Expected format: Bearer gsk_xxxxxxxxxxxxx
    """
    api_key = credentials.credentials
    
    # Validasi format API key (Groq keys start with 'gsk_')
    if not api_key.startswith('gsk_'):
        raise HTTPException(
            status_code=401, 
            detail="Invalid API key format. Groq API keys should start with 'gsk_'"
        )
    
    return api_key

@app.get("/", tags=["Health Check"])
def read_root():
    """Health check endpoint"""
    return {
        "message": "Stock Analysis Service is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.post(
    "/analyze_stock/", 
    tags=["Analysis Service"],
    response_model=StockAnalysisResponse
)
def analyze_stock(
    request: StockAnalysisRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Analyze stock fundamentals using Groq AI
    
    **Authorization**: Bearer token required (your Groq API key)
    
    **Example**:
    ```
    Headers:
    Authorization: Bearer gsk_your_api_key_here
    
    Body:
    {
        "input_text": "Analyze Apple stock performance"
    }
    ```
    """
    try:
        stock_agent = StockFundamentalAgent(api_key=api_key)
        analyst = stock_agent.run(request.input_text)
        
        return StockAnalysisResponse(
            status="success",
            data=analyst
        )
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(ve)}")
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Analysis failed: {str(e)}"
        )

@app.get("/health", tags=["Health Check"])
def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "Stock Analysis",
        "environment": os.getenv("ENVIRONMENT", "production")
    }