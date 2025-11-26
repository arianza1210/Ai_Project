import streamlit as st
import asyncio
import base64
from pathlib import Path
import sys, os

# ===== IMPORT AGENT (Assumes agent module is available) =====
# Pastikan modul 'agent.test' tersedia di lingkungan Anda
try:
    from agent.Agent_StockAnalysis   import StockFundamentalAgent
except ImportError:
    st.error("❌ Modul 'agent.test.StockFundamentalAgent' tidak ditemukan. Pastikan path impor sudah benar.")
    class StockFundamentalAgent:
        def __init__(self, api_key): pass
        def run(self, query): return "Simulasi respons karena StockFundamentalAgent tidak dapat diimpor."


# ========== CONFIG PAGE ==========
st.set_page_config(
    page_title="Stock Analysis Chatbot",
    page_icon="📈",
    layout="wide"
)

# ========== CSS CHAT BUBBLE (Hanya untuk User) ==========
st.markdown("""
    <style>
    /* Wrapper untuk mengatur posisi (kanan/kiri) */
    .bubble-wrapper {
        display: flex;
        width: 100%;
        margin-bottom: 10px;
    }
    /* User: Posisikan ke kanan */
    .user-wrap { 
        justify-content: flex-end; 
    }

    /* Styling dasar bubble */
    .chat-bubble {
        padding: 12px 16px;
        border-radius: 14px;
        max-width: 85%;
        /* Warna default (tidak terlihat karena user-bubble override) */
        background: #f2f2f2; 
        border: 1px solid #ddd;
        /* Penting: Pastikan konten markdown di dalamnya tidak terpotong */
        word-wrap: break-word; 
        overflow-wrap: break-word;
    }
    /* User: Gaya khusus bubble */
    .user-bubble {
        background-color: #0084ff;
        color: white;
        border: none;
        box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    /* Tambahan style untuk kontainer full-width assistant response jika diperlukan */
    .st-emotion-cache-1ftn5tq { /* Class Streamlit untuk block container */
        padding: 0;
    }

    </style>
""", unsafe_allow_html=True)


# ========== SIDEBAR SETTING ==========
st.sidebar.header("🔐 API Settings")

api_key = st.sidebar.text_input(
    "Masukkan Groq API Key:",
    type="password",
    placeholder="grq-xxxxxxxxxxxxxxxx"
)

st.sidebar.markdown("---")
st.sidebar.markdown("📊 **Stock Analysis Chatbot**\nby Pandi")


# ========== SESSION STATE ==========
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    st.session_state.agent = None


# ========== INIT AGENT ==========
if api_key and st.session_state.agent is None:
    try:
        # Coba inisialisasi agen dengan kunci API yang diberikan
        st.session_state.agent = StockFundamentalAgent(api_key)
    except Exception as e:
        st.error(f"❌ Error saat inisialisasi agent. Pastikan Groq API Key valid dan StockFundamentalAgent berfungsi: {e}")


# ========== HEADER ==========
st.markdown("<h1>📈 Stock Analysis Chatbot</h1>", unsafe_allow_html=True)
st.write("Tanyakan apa saja tentang analis saham IDX (teknikal, fundamental, rekomendasi, tren pasar).")


# ======== CHECK API KEY ========
if not api_key:
    st.warning("⚠️ Masukkan API key di sidebar untuk mulai menggunakan chatbot.")
    st.stop()


# ======== FUNCTION RENDER CHAT (DIPERBAIKI) ========
def render_message(role, content):
    if role == "user":
        # Render pesan User sebagai bubble di kanan
        wrap_class = "user-wrap"
        bubble_class = "user-bubble"
        
        # FIX: Gabungkan seluruh struktur HTML bubble dan konten ke dalam satu st.markdown
        st.markdown(
            f"""
            <div class='bubble-wrapper {wrap_class}'>
                <div class='chat-bubble {bubble_class}'>
                    {content}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # Render pesan Assistant sebagai full markdown view (tidak ada bubble)
        # Gunakan st.markdown langsung, diikuti separator untuk kejelasan
        st.markdown(content)
        st.markdown("---")


# ======== SHOW HISTORY ========
for msg in st.session_state.messages:
    render_message(msg["role"], msg["content"])


# ======== INPUT PROMPT ========
user_input = st.chat_input("Ketik pertanyaan saham Anda...")

if user_input:
    # Simpan pesan pengguna
    st.session_state.messages.append({"role": "user", "content": user_input})
    render_message("user", user_input)

    # Jawaban
    with st.spinner("🔎 Menganalisis data saham..."):
        try:
            if st.session_state.agent:
                 reply = st.session_state.agent.run(user_input)
            else:
                 reply = "⚠️ Agen Analisis Saham belum berhasil diinisialisasi. Periksa API Key Anda."
        except Exception as e:
            reply = f"⚠️ Terjadi Error saat menjalankan agent: {e}"

    # Simpan + tampilkan jawaban asisten
    st.session_state.messages.append({"role": "assistant", "content": reply})
    render_message("assistant", reply)

    # Auto scroll (opsional, untuk pengalaman chatting)
    # Ini memerlukan trik JavaScript, yang mungkin diblokir di beberapa lingkungan.
    # st.markdown(
    #     "<script>window.scrollTo(0, document.body.scrollHeight);</script>",
    #     unsafe_allow_html=True
    # )