from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.memory import MemoryManager
from agno.models.groq import Groq
from agno.tools.yfinance import YFinanceTools
from agno.tools.duckduckgo import DuckDuckGoTools
from rich.pretty import pprint
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY", "")
if not API_KEY:
    raise ValueError("GROQ_API_KEY belum diset")

agent_db = SqliteDb(db_file="tmp/agents.db")
memory_manager = MemoryManager(
    model=Groq(id="qwen/qwen3-32b"),
    db=agent_db,
    additional_instructions="Simpan: asset favorit, risk tolerance, timeframe, strategi.",
)
instructions = """
Kamu adalah **AI Multi-Asset Analyst** untuk:
- 🇮🇩 Saham IDX (BBCA.JK)
- 🪙 Komoditas (GC=F, CL=F) 
- 💱 Forex (EURUSD=X)
- 🪙 Crypto (BTC-USD)

## ATURAN KETAT
1. Jika user sebut kode → LANGSUNG analisis
2. Gunakan HANYA data dari tools (jangan hitung ulang)
3. DuckDuckGo: MAKSIMAL 1-2 query, kata kunci singkat
4. Bahasa Indonesia, profesional, data-driven

## METODOLOGI (SINGKAT)

### Teknikal (WAJIB)
Gunakan data YFinance: SMA, EMA, RSI, MACD, Stochastic, Fibo Levels (R1-R3, S1-S3), Volume Ratio.
Identifikasi: Trend, Momentum, Support/Resistance.

### Fundamental (Saham Only)
PER, PBV, ROE, DER, EPS, Revenue Growth.

### Sentimen (via DuckDuckGo)
1 query berita 7 hari: "[symbol] news today"
Sentimen: POSITIF/NEGATIF/NETRAL

## OUTPUT FORMAT (RINGKAS)

# 📈 [ASSET]

## Ringkasan
[1-2 kalimat: Trend + Sentimen + Rekomendasi]

## Teknikal
**Trend**: [Bullish/Bearish/Sideways]
- MA: [posisi harga vs MA]
- RSI: [overbought/oversold/netral]
- MACD: [bullish/bearish cross]
- Support/Resistance: [levels penting]
- Fibo: [R1-R3, S1-S3]

## Fundamental (jika saham)
**Rating**: [Kuat/Wajar/Lemah]
- Valuasi: [PER/PBV]
- Profit: [ROE/Margin]

## Sentimen
**Sentimen**: [Positif/Negatif/Netral]
- Berita: [1-2 poin penting]

## Rekomendasi
**Action**: [BUY/HOLD/SELL/WAIT]
- Entry: [harga]
- TP: [harga] (+[%])
- SL: [harga] (-[%])
- R:R: [ratio]
- Alasan: [singkat]

⚠️ Bukan nasihat keuangan.

## CATATAN FIBONACCI
- Pivot = (H+L+C)/3, Range = H-L
- R1 = P+0.382*R, R2 = P+0.618*R, R3 = P+1.0*R
- S1 = P-0.382*R, S2 = P-0.618*R, S3 = P-1.0*R

Padat, jelas, efisien token.
"""
user_id = "pandi@gmail.com"

agent_optimized = Agent(
    name="AI Multi-Asset Analyst",
    model=Groq(id="openai/gpt-oss-20b"),
    instructions=instructions,
    tools=[YFinanceTools(), DuckDuckGoTools()],
    db=agent_db,
    memory_manager=memory_manager,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=3,  # Reduced from 5
    markdown=True # Hide tool calls to save tokens
)
def quick_technical_analysis(symbol: str):
    """Analisis cepat hanya teknikal, tanpa berita (hemat token)"""
    prompt = f"Analisis teknikal {symbol} saja, skip berita untuk hemat token."
    agent_optimized.print_response(prompt, user_id=user_id, stream=True)

def full_analysis(symbol: str):
    """Analisis lengkap dengan berita"""
    prompt = f"Analisis lengkap {symbol}"
    agent_optimized.print_response(prompt, user_id=user_id, stream=True)
if __name__ == "__main__":
    # Set preferensi (singkat)
    # agent_optimized.print_response(
    #     "Saya swing trader, risk sedang, fokus komoditas.",
    #     user_id=user_id,
    #     stream=True,
    # )
    
    # print("\n" + "="*60 + "\n")
    
    # Quick analysis (hemat token)
    print("🚀 Quick Technical Analysis (No News)")
    quick_technical_analysis("BKSL.jk")
    
    print("\n" + "="*60 + "\n")
    
    # Full analysis with news
    # print("📰 Full Analysis (With News)")
    # full_analysis("BTC-USD")
    
    # print("\n" + "="*60 + "\n")
    
    # # Forex analysis
    # agent_optimized.print_response(
    #     "EURUSD=X setup trading besok",
    #     user_id=user_id,
    #     stream=True,
    # )

    # Check memory
    memories = agent_optimized.get_user_memories(user_id=user_id)
    print("\n" + "=" * 60)
    print("MEMORY")
    print("=" * 60)
    pprint(memories)