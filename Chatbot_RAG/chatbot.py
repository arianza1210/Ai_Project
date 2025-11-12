import streamlit as st
import os
from pathlib import Path
import asyncio
import base64
from src.llm_process import LLMProcess
from src.wrapper import llm_wrapper
from src.create_faiss import KnowledgeBaseManager

# ======== Import Ragas for Evaluation ========
from ragas import evaluate
from ragas.metrics import faithfulness, context_recall, context_precision  #answer_relevancy
from datasets import Dataset

st.set_page_config(page_title="UNS Chatbot", page_icon="🤖", layout="wide")

menu = st.sidebar.radio("Pilih Mode", ["Chatbot", "Evaluasi RAGAS"])

# ======== CSS Kustom ========
st.markdown("""
    <style>
    .chat-bubble {
        padding: 10px 15px;
        margin: 5px;
        border-radius: 15px;
        word-wrap: break-word;
        display: inline-block;
        max-width: 90%; /* dari 60% jadi 90% */
    }
    .user-bubble {
        background-color: #0084ff;
        color: white;
    }
    .assistant-bubble {
        background-color: #e5e5ea;
        color: black;
    }
    @media (max-width: 768px) {
        .chat-bubble {
            max-width: 100%;
        }
    }
    </style>
""", unsafe_allow_html=True)


def auto_height_text_area(label, value):
    lines = value.count("\n") + 1
    height = min(600, max(100, lines * 20)) 
    return st.text_area(label, value=value, height=height)

assets_path = Path(__file__).resolve().parent / "assets"
logo_path = assets_path / "Logo-UNS-New-04-1-300x300.png"
with open(logo_path, "rb") as f:
    logo_base64 = base64.b64encode(f.read()).decode()

st.markdown(
    f"""
    <div style='display: flex; align-items: center;'>
        <img src='data:image/png;base64,{logo_base64}' width='70' style='margin-right: 10px;'>
        <h1 style='margin: 0;'>UNS Customer Service Chatbot</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# ======== Mode Chatbot ========
if menu == "Chatbot":
    if "llm" not in st.session_state:
        st.session_state.llm = LLMProcess()
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]

        if role == "user":
            st.markdown(
                f"""
                <div style='display: flex; justify-content: flex-end;'>
                    <div class='chat-bubble user-bubble'>{content}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div style='display: flex; justify-content: flex-start;'>
                    <div class='chat-bubble assistant-bubble'>{content}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    if prompt := st.chat_input("Ketik pertanyaan Anda di sini..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        st.markdown(
            f"""
            <div style='display: flex; justify-content: flex-end;'>
                <div class='chat-bubble user-bubble'>{prompt}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.spinner("Sedang memproses jawaban..."):
            try:
                bot_reply = asyncio.run(st.session_state.llm.generate_response(prompt))
            except Exception as e:
                bot_reply = f"⚠️ Terjadi kesalahan: {e}"

        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

        st.markdown(
            f"""
            <div style='display: flex; justify-content: flex-start;'>
                <div class='chat-bubble assistant-bubble'>{bot_reply}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

# ======== Mode Evaluasi RAGAS ========
elif menu == "Evaluasi RAGAS":
    st.subheader("Evaluasi Kualitas Jawaban (RAGAS)")
    st.markdown("""
    Evaluasi ini mengukur kualitas jawaban chatbot berdasarkan beberapa metrik:
    - **Faithfulness**: Mengukur seberapa konsisten dan faktual jawaban terhadap informasi yang ada di konteks. 
    - **Context Recall**: Seberapa baik konteks yang relevan diingat oleh chatbot.
    - **Context Precision**: Seberapa tepat konteks yang digunakan dalam jawaban.
    """)
    # answer_relevancy.llm = llm_wrapper
    faithfulness.llm = llm_wrapper
    context_precision.llm = llm_wrapper
    context_recall.llm = llm_wrapper

    if "messages" in st.session_state and len(st.session_state.messages) >= 2:
        last_user_msg = next((m["content"] for m in reversed(st.session_state.messages) if m["role"] == "user"), "")
        last_bot_msg = next((m["content"] for m in reversed(st.session_state.messages) if m["role"] == "assistant"), "")
    else:
        last_user_msg = ""
        last_bot_msg = ""

    context= KnowledgeBaseManager().get_relevant_context(last_user_msg)
    context_text = "\n\n".join(
            [f"Dokumen {i+1}:\n{ctx['text']}" for i, ctx in enumerate(context)]
        )
    
    question = st.text_area("Pertanyaan", value=last_user_msg)
    ground_truth = st.text_area("Jawaban Benar", height=200)
    generated_answer = st.text_area("Jawaban Chatbot", value=last_bot_msg, height=250)
    retrieved_context = st.text_area("Konteks yang Diambil", value=context_text, height=250)

    if st.button("Hitung Skor RAGAS"):
        if not all([question, ground_truth, generated_answer, retrieved_context]):
            st.warning("⚠️ Isi semua field ya.")
        else:
            data = Dataset.from_dict({
                "question": [question],
                "answer": [generated_answer],
                "contexts": [[retrieved_context]],
                "ground_truth": [ground_truth]
            })
            scores = evaluate(
                data,
                metrics=[faithfulness, context_recall, context_precision]
            )
            st.success("✅ Evaluasi selesai!")


            df_scores = scores.to_pandas()

            metric_columns = ["faithfulness", "context_recall", "context_precision"]
            scores_dict = {col: float(df_scores[col][0]) for col in metric_columns}
            
            st.markdown("### Skor Evaluasi:")
            col1, col2, col3 = st.columns(3)
            col1.metric("Faithfulness", f"{scores_dict['faithfulness']:.2f}")
            col2.metric("Context Recall", f"{scores_dict['context_recall']:.2f}")
            col3.metric("Context Precision", f"{scores_dict['context_precision']:.2f}")