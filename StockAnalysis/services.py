from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import os

from agent.Agent_StockAnalysis import StockFundamentalAgent

# =========================
# App & Security
# =========================
app = FastAPI(
    title="Stock Analysis Service",
    version="1.0.0"
)

security = HTTPBearer()

# =========================
# CORS (optional)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Models
# =========================
class StockAnalysisRequest(BaseModel):
    input_text: str

    class Config:
        json_schema_extra = {
            "example": {
                "input_text": "Analyze AAPL stock fundamentals"
            }
        }


class StockAnalysisResponse(BaseModel):
    status: str
    data: str


# =========================
# Auth Dependency
# =========================
def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Authorization: Bearer gsk_xxxxx
    """
    api_key = credentials.credentials

    if not api_key.startswith("gsk_"):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key format"
        )

    return api_key


# =========================
# Routes
# =========================
@app.get("/", tags=["Health Check"])
def root():
    return {
        "message": "Stock Analysis Service is running",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.post(
    "/analyze_stock",
    response_model=StockAnalysisResponse,
    tags=["Analysis Service"]
)
def analyze_stock(
    request: StockAnalysisRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Analyze stock fundamentals using Groq AI

    Authorization:
    Bearer gsk_xxxxxxxxxx
    """
    try:
        agent = StockFundamentalAgent(api_key=api_key)
        result = agent.run(request.input_text)

        return StockAnalysisResponse(
            status="success",
            data=result
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.get("/health", tags=["Health Check"])
def health():
    return {
        "status": "healthy",
        "service": "Stock Analysis",
        "environment": os.getenv("ENVIRONMENT", "production")
    }
