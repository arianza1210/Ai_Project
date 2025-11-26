#runing uvicorn command: uvicorn services:app --host 0.0.0.0 --port {your_port}


from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os , sys

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(backend_path)
from agent.Agent_StockAnalysis import StockFundamentalAgent

app = FastAPI(title="Stock Analysis Service", version="1.0.0")
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "http://localhost:3002",
    "http://127.0.0.1:3002",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


#global instance of stock agent
stock_agent = StockFundamentalAgent()

@app.get("/",tags=["Analysis Service"])
def read_root():
    return {"message": "Stock Analysis Service is running."}


@app.post("/analyze_stock/", tags=["Analysis Service"])
def analyze_stock(input_text: str):
    try:
        analyst= stock_agent.run(input_text)
        result={
            "status": "success",
            "data": analyst
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


