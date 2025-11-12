from agno.models.groq import Groq
from agno.agent import Agent
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

class AnswerSchema(BaseModel):
    answer: str = Field(..., description="Jawaban terkait instruksi yang diberikan")

class GeneralAgent:
    def __init__(self):
        self._init_agents()
    
    def _init_agents(self):
        self.agent_general = Agent(
            name="General Agent QnA",
            role="You are an AI assistant that answers questions clearly and concisely.",
            model=Groq(
                id="meta-llama/llama-4-scout-17b-16e-instruct",
                api_key=API_KEY
            ),
            instructions=[
                "Jawab pertanyaan pengguna dengan bahasa yang alami dan mudah dipahami.",
                "Jika pertanyaannya umum, beri jawaban ringkas tapi informatif.",
                "Jika pertanyaannya teknis, berikan langkah atau penjelasan singkat."
            ],
            output_schema=AnswerSchema,
            use_json_mode=True
        )
    
    def run(self, question: str):
        result = self.agent_general.run(question)
        return result.content.model_dump()
    
if __name__=="__main__":
    agent=GeneralAgent()
    question="hallo apa kabar?"
    result=agent.run(question)
    print(result)