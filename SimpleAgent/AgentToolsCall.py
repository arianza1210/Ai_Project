import os
from textwrap import dedent
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
from pydantic import BaseModel, Field

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY", "")

class AnswerSchema(BaseModel):
    answer: str = Field(..., description="Jawaban dari pertanyaan yang diberikan")

class AgentQnA:
    def __init__(self):
        self._init_agent()
    
    def _init_agent(self):
        self.agent= Agent(
            name="Agent QnA",
            model=Groq(
                id="meta-llama/llama-4-scout-17b-16e-instruct",
                api_key= API_KEY
            ),
            instructions=dedent("""
                Kamu adalah seorang assistant yang ditugaskan menjawab pertanyaan user.
                Jika kamu tidak tahu, cari menggunakan tools pencarian.
            """),
            tools=[DuckDuckGoTools(timeout=200)],
            use_json_mode=False
        )

    def ask(self, query: str):
        result= self.agent.run(query)
        return result.content

if __name__=="__main__":
    agent = AgentQnA()
    response = agent.ask("siapakah presiden Indonesia sekarang ini 2025 ?")
    print(response)
