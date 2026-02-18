import os
from textwrap import dedent
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.groq import Groq
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

class SelectAgentTeam():
    def __init__(self):
        self.model_id = "meta-llama/llama-4-scout-17b-16e-instruct" 
        
        self.agent_research = Agent(
            name="Research Agent",
            role="Research Analysis",
            model=Groq(id=self.model_id, api_key=api_key),
            instructions=dedent("""
                Kamu adalah agent pencarian yang sangat teliti.
                Tugas:
                - Cari fakta terbaru dan paling relevan mengenai wisata.
                - Ambil dari minimal 2 sumber berbeda.
                - Kembalikan hasil pencarian mentah & link sumber.
                Format jawaban:
                - Bullet points.
                - Sertakan link URL mentah.
            """),
            tools=[DuckDuckGoTools(timeout=200)],
            markdown=True,
        )

        self.agent_analyst = Agent(
            name="Analyst Agent",
            role="Analysis Agent",
            model=Groq(id=self.model_id, api_key=api_key),
            instructions=dedent("""
                Kamu adalah agent analisis yang sangat teliti.
                Tugas:
                - Analisis hasil pencarian dari Research Agent.
                - Verifikasi kecocokan antar sumber.
                - Tandai jika ada informasi yang bertentangan.
                Format jawaban:
                - Ringkasan yang rapi.
                - Sertakan link sumber mentah.
            """),
            markdown=True,
        )

    def run(self, query: str, session_state: dict):

        need_analysis = session_state.get("need_analysis", False)
        agents = [self.agent_research, self.agent_analyst] if need_analysis else [self.agent_research]

        team = Team(
            name="Agent Selection Analysis",
            model=Groq(id=self.model_id, api_key=api_key),
            members=agents,
            instructions=dedent("""
                Koordinasikan tim untuk menjawab pertanyaan user.
                Pastikan informasi akurat dan sumber disertakan.
            """),
            markdown=True,
        )
        
        return team.print_response(query)

if __name__ == "__main__":
    agent_team = SelectAgentTeam()
    agent_team.run("Di kabupaten pesawaran ada wisata apa saja", {"need_analysis": True})