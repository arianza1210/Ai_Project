import streamlit as st
import asyncio
import base64
from pathlib import Path
import sys, os

# ===== IMPORT AGENT =====
try:
    from agent.Agent_StockGeneral import StockFundamentalAgent
except ImportError:
    st.error("❌ Modul 'agent.Agent_StockGeneral.StockFundamentalAgent' tidak ditemukan. Pastikan path impor sudah benar.")
    class StockFundamentalAgent:
        def __init__(self, api_key, model="auto"): pass
        def run(self, query): 
            return "⚠️ Simulasi respons karena StockFundamentalAgent tidak dapat diimpor."

# ===== LIST MODEL =====
LIST_MODEL = {
    "auto": "openai/gpt-oss-120b",
    "qwen3-32b": "qwen/qwen3-32b",
    "llama-4-scout-17b": "meta-llama/llama-4-scout-17b-16e-instruct",
    "openai-gpt-120b": "openai/gpt-oss-120b",
    "openai-oss-20b": "openai/gpt-oss-20b"
}

# ========== CONFIG PAGE ==========
st.set_page_config(
    page_title="Stock Analysis General Chatbot",
    page_icon="📈",
    layout="wide"
)

# ========== SIDEBAR ==========
st.sidebar.header("🔐 API & Model Settings")

api_key = st.sidebar.text_input(
    "Masukkan Groq API Key:",
    type="password",
    placeholder="grq-xxxxxxxxxxxxxxxx"
)

model_choice = st.sidebar.selectbox(
    "Pilih Model",
    list(LIST_MODEL.keys()),
    index=0 
)

model_used = LIST_MODEL[model_choice]

st.sidebar.markdown(f"✅ **Model Aktif:** `{model_choice}`")
st.sidebar.markdown("---")
st.sidebar.markdown("📊 **Stock Analysis General Chatbot**")

# ========== SESSION STATE ==========
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    st.session_state.agent = None

if "last_model" not in st.session_state:
    st.session_state.last_model = model_choice

# ========== RESET AGENT JIKA MODEL BERUBAH ==========
if st.session_state.last_model != model_choice:
    st.session_state.agent = None
    st.session_state.last_model = model_choice

# ========== INIT AGENT ==========
if api_key and st.session_state.agent is None:
    try:
        st.session_state.agent = StockFundamentalAgent(
            api_key=api_key,
            model=model_used 
        )
        st.sidebar.success(f"✅ Agent aktif dengan model: {model_choice}")
    except Exception as e:
        st.error(f"❌ Error saat inisialisasi agent: {e}")

# ========== HEADER ==========
st.markdown("<h1>📈 Stock Analysis General Chatbot</h1>", unsafe_allow_html=True)
st.write(
    "Tanyakan apakah tentang **saham IDX & global** "
    "(teknikal, fundamental, rekomendasi, tren pasar).\n\n"
    "📌 *Jika saham IDX, tambahkan `.JK` di belakang symbol.*"
)

# ======== CHECK API KEY ========
if not api_key:
    st.warning("⚠️ Masukkan API key di sidebar untuk mulai menggunakan chatbot.")
    st.stop()

# ========== RENDER CHAT ==========
def render_message(role, content):
    if role == "user":
        st.markdown(
            f"""
            <div style='display:flex; justify-content:end; margin-bottom:10px;'>
                <div style='
                    background:#0084ff;
                    color:white;
                    padding:10px 14px;
                    border-radius:14px;
                    max-width:80%;
                    '>
                    {content}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(content)
        st.markdown("---")

# ======== SHOW HISTORY ========
for msg in st.session_state.messages:
    render_message(msg["role"], msg["content"])

# ======== INPUT PROMPT ========
user_input = st.chat_input("Ketik pertanyaan saham Anda...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    render_message("user", user_input)

    with st.spinner(f"🔎 Menganalisis dengan model `{model_choice}`..."):
        try:
            if st.session_state.agent:
                reply = st.session_state.agent.run(user_input)
            else:
                reply = "⚠️ Agent belum berhasil diinisialisasi."
        except Exception as e:
            reply = f"⚠️ Terjadi Error saat menjalankan agent: {e}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    render_message("assistant", reply)
