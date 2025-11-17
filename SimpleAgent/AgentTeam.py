import os, sys, json
from textwrap import dedent
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.team import Team


load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")


class BaseLocationAgent:
    def __init__(self):
        self._init_agent()

    def _init_agent(self):
        self.agent_search = Agent(
            name="Agent Search",
            model=Groq(id="meta-llama/llama-4-scout-17b-16e-instruct", api_key=API_KEY),
            tools=[DuckDuckGoTools(timeout=200)],
            instructions=dedent(
                """\
                kamu adalah agent pencarian yang sangat teliti.
                 Tugas:
                - Cari fakta terbaru dan paling relevan
                - Ambil dari minimal 2 sumber berbeda
                - Kembalikan hasil pencarian mentah & link sumber
                Format jawaban:
                - Bullet points
                - Sertakan link sumber. **JANGAN gunakan format [teks](link), gunakan link URL mentah.**"""
            ),
            markdown=True,
        )

        self.agent_fact = Agent(
                name="Agent Fact",
                model=Groq(id="meta-llama/llama-4-scout-17b-16e-instruct", api_key=API_KEY),
                instructions=dedent(
                    """
            Kamu adalah analis fakta.
            Tugas:
            - Gabungkan hasil pencarian
            - Verifikasi kecocokan antar sumber
            - Tandai jika ada informasi yang bertentangan
            - Hanya ambil fakta yang konsisten
            
            Output:
            - **Formatkan output kamu sebagai TEXT BIASA (non-JSON, non-function call)**
            - **Bagian 1:** Fakta utama (gunakan bullet points).
            - **Bagian 2:** Kesimpulan verifikasi (1-2 kalimat deskriptif).
            """
                ),
                markdown=True,
            )
        
        self.lead_team_agent = Team(
            members=[self.agent_search, self.agent_fact],
            model=Groq(id="meta-llama/llama-4-scout-17b-16e-instruct", api_key=API_KEY),
            instructions=dedent(
                """
        Kamu adalah Lead Answerer.
        Tugas:
        - Gabungkan hasil Search Specialist + Fact Analyst
        - Buat jawaban yang ringkas, akurat, dan mudah dibaca
        - Jika ada data yang belum pasti, beri catatan
        Format:
        - Jawaban utama (1–3 kalimat)
        - Fakta pendukung (bullet points)
        - Sumber (link URL mentah, **JANGAN gunakan format Markdown [teks](link)**)
    """
            ),
            show_members_responses=False,
            markdown=True
        )
        
    def run(self, query:str):
        result=self.lead_team_agent.run(query)
        return result.content
    
    
if __name__=="__main__":
    agent=BaseLocationAgent()
    result= agent.run("kandang persija jakarta dimana?")
    print(result)
