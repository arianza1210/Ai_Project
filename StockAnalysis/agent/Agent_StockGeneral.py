# agent/Agent_StockAnalysis.py

from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.team import Team
import os, sys
from datetime import datetime
from dotenv import load_dotenv
from textwrap import dedent

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append((backend_dir))
from utils.get_yfinance import YFinance
from models import ListSaham
from agent.prompt.prompt import (
    TECHNICAL_ANALYSIS_PROMPT,
    FUNDAMENTAL_ANALYSIS_PROMPT,
    TRADING_RECOMMENDATION_PROMPT,
    MARKET_TREND_NEWS_PROMPT,
    GENERAL_ANALYSIS_PROMPT
)


class StockFundamentalAgent:
    def __init__(self, api_key):
        self.API_KEY=api_key
        self._init_agent()
        self.extract_yfinance = YFinance()

    def _init_agent(self):
        self.extract_saham_agent = Agent(
            name="ExtractSahamAgent",
            model=Groq(id="openai/gpt-oss-120b", api_key=self.API_KEY),
            system_message="anda adalah asisten yang mengekstrak kode saham dari teks input. jika saham indonesia ditambahkan .JK diakhir (jika belum ada). jika tidak ada saham, kembalikan string kosong output dalam bentuk json dengan format {'symbols': []}",
            output_schema=ListSaham,
            use_json_mode=True,
        )
        
        self.technical_analysis_agent = Agent(
            name="TechnicalAnalysisAgent",
            model=Groq(id="openai/gpt-oss-120b", api_key=self.API_KEY),
            instructions=TECHNICAL_ANALYSIS_PROMPT,
            use_json_mode=False,
        )
        
        self.fundamental_analysis_agent = Agent(
            name="FundamentalAnalysisAgent",
            model=Groq(id="openai/gpt-oss-120b", api_key=self.API_KEY),
            instructions=FUNDAMENTAL_ANALYSIS_PROMPT,
            use_json_mode=False,
        )
        
        self.trading_recommendation_agent = Agent(
            name="TradingRecommendationAgent",
            model=Groq(id="openai/gpt-oss-120b", api_key=self.API_KEY),
            instructions=TRADING_RECOMMENDATION_PROMPT,
            use_json_mode=False,
        )
        
        self.market_trend_news_agent = Agent(
            name="MarketTrendNewsAgent",
            model=Groq(id="openai/gpt-oss-120b", api_key=self.API_KEY),
            tools=[DuckDuckGoTools(timeout=2000, fixed_max_results=5)],
            instructions=MARKET_TREND_NEWS_PROMPT,
            use_json_mode=False,
        )
        self.general_analysis_agent = Agent(
            name="GeneralAnalysisAgent",
            model=Groq(id="openai/gpt-oss-120b", api_key=self.API_KEY),
            tools=[DuckDuckGoTools(timeout=2000, fixed_max_results=5)],
            instructions=GENERAL_ANALYSIS_PROMPT,
            use_json_mode=False,
        )
        
        self.lead_agent = Team(
            members=[
                self.technical_analysis_agent,
                self.fundamental_analysis_agent,
                self.trading_recommendation_agent,
                self.market_trend_news_agent,
                self.general_analysis_agent
            ],
            model=Groq(id="openai/gpt-oss-120b", api_key=self.API_KEY),
            instructions=dedent("""\
                Anda adalah Lead Orchestrator Agent yang bertugas menganalisis pertanyaan pengguna dan memilih agent paling relevan untuk kasus saham global. Jika ticker saham mengandung akhiran .JK, maka rute analisis harus diarahkan ke IDX (Bursa Efek Indonesia). Jika tidak, gunakan agent saham global.
                
                Aturan pemilihan:
                - Jika user menanyakan "tren pasar", "market trend", "berita pasar", "sentimen pasar", 
                atau kata yang menunjukkan analisis berbasis berita → pilih MarketTrendNewsAgent.
                
                - Jika user meminta rekomendasi saham **yang bergantung pada tren pasar atau berita**, 
                misalnya: "rekomendasi untuk besok", "saham bagus besok", "saham potensial minggu ini"
                → tetap gunakan MarketTrendNewsAgent karena butuh pencarian berita dan sentimen.

                - Jika user hanya menanyakan "teknikal", "indikator", "chart", "support-resistance" → TechnicalAnalysisAgent.

                - Jika user hanya menanyakan "fundamental", "laporan keuangan", "EPS", "balance sheet" → FundamentalAnalysisAgent.

                - Jika user menanyakan "rekomendasi", "analisis" tanpa konteks berita → TradingRecommendationAgent.

                - Jika pertanyaan tidak jelas → GeneralAnalysisAgent.

                Seluruh output HARUS dalam MARKDOWN dan gunakan bahasa Indonesia.
"""),
            show_members_responses=False,
            markdown=True
        )

    def extract_saham(self, user_input: str):
        response = self.extract_saham_agent.run(user_input)
        return response.content.model_dump()

    def extract_yfinance_data(self, symbols: list[str]):
        results = []
        for tk in symbols:
            data = self.extract_yfinance.format_stock_data(tk)
            if "full_markdown" in data:
                results.append(data["full_markdown"])
            else:
                results.append(f"### {tk}\nError: {data['error']}")
        return "\n\n---\n\n".join(results)

    def run(self, user_input: str):
        saham_list = self.extract_saham(user_input)
        symbols = saham_list.get("symbols", [])

        yfinance_data = self.extract_yfinance_data(symbols=symbols)
        date_now = datetime.now().strftime("%Y-%m-%d")
        prompt = f"""Tanggal Hari ini: {date_now}
Berikut adalah data yfinance untuk saham: {', '.join(symbols)}\n\n{yfinance_data}
berikut adalah pertanyaan user: {user_input}
Analisis dan berikan rekomendasi berdasarkan data di atas.

note: 
- jawaban harus dalam MARKDOWN.
- jika user menayakan besok maka tanggal hari ini ditambah 1 hari.
        """
        result = self.lead_agent.run(prompt)
        return result.content.strip()


if __name__ == "__main__":
    agent = StockFundamentalAgent()
    query = "buatkan saya tren pasar dan rekomendasi untuk saham yang bagus besok"
    result = agent.run(query)
    print(result)
