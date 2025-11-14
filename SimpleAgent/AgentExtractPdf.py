from agno.models.groq import Groq
from agno.agent import Agent
import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import pdfplumber


load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

class PDFExtractSchema(BaseModel):
    answer: str = Field(..., description="Hasil ekstraksi atau jawaban berdasarkan isi PDF")

class PDFExtractorAgent:
    def __init__(self):
        self._init_agent()

    def _init_agent(self):
        self.agent = Agent(
            name="PDF Extractor Agent",
            role="You are an AI agent specialized in reading and extracting information from PDF files.",
            model=Groq(
                id="meta-llama/llama-4-scout-17b-16e-instruct",
                api_key=API_KEY
            ),
            instructions=[
                "Pengguna akan memberikan teks hasil ekstraksi PDF.",
                "Berikan jawaban yang ringkas, akurat, dan fokus pada instruksi pengguna.",
                "Jika pengguna meminta ringkasan, berikan ringkasan terbaik.",
                "Jika pengguna meminta poin penting, buatkan poin-poinnya.",
                "Jika pengguna meminta ekstraksi data, ambil hanya data pentingnya."
            ],
            output_schema=PDFExtractSchema,
            use_json_mode=True
        )

    def _read_pdf(self, pdf_path: str) -> str:
        all_text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                all_text += text + "\n"
        return all_text.strip()

    def extract(self, pdf_path: str, instruction: str):
        pdf_text = self._read_pdf(pdf_path)

        prompt = f"""
Berikut adalah isi PDF:

--------------------
{pdf_text}
--------------------

Instruksi pengguna: {instruction}

Berikan jawaban sesuai instruksi.
"""
        result = self.agent.run(prompt)
        return result.content.model_dump()

if __name__ == "__main__":
    agent = PDFExtractorAgent()

    pdf_file = "data/artikel+74+RAHELLEA+ANDERA+700-709.pdf"
    # instruction = "Ringkas isi dokumen ini menjadi 5 poin."
    instruction="siapakah yang membuat artikel ini"
    
    result = agent.extract(pdf_file, instruction)
    print(json.dumps(result, indent=2))
