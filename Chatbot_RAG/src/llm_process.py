from groq import Groq
from typing import List, Dict, Any
from json_repair import loads
import os
from pathlib import Path
from dotenv import load_dotenv
from .prompt import PROMPT_COSTUMER_SERVICE
from .create_faiss import KnowledgeBaseManager

# --- Load .env dari root project ---
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class LLMProcess:
    def __init__(self):
        self.llm = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.llm_model_name = "meta-llama/llama-4-scout-17b-16e-instruct"
        self.kb_manager = KnowledgeBaseManager()
             
    def _get_prompt(self, query: str, contexts: List[Dict[str, Any]]) -> str:
        system_prompt = """You are a customer service chatbot for Universitas Sebelas Maret (UNS) Surakarta. 
        You assist users with questions about university services, academic programs, and general information about UNS."""
        
        context_text = "\n\n".join(
            [f"Dokumen {i+1}:\n{ctx['text']}" for i, ctx in enumerate(contexts)]
        )
        user_prompt = PROMPT_COSTUMER_SERVICE.format(query=query, context=context_text)
        
        return system_prompt, user_prompt
    
    async def generate_response(self, query: str) -> str:
        try:
            contexts = self.kb_manager.get_relevant_context(query)
            if not contexts:
                return "Maaf, saya tidak memiliki informasi yang relevan untuk pertanyaan Anda. Silakan hubungi departemen terkait untuk bantuan lebih lanjut."
            system_prompt, user_prompt = self._get_prompt(query, contexts)
            completion = self.llm.chat.completions.create(
                model=self.llm_model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1028,
                temperature=0.7
            )
            
            response = completion.choices[0].message.content.strip()
            return response
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Maaf, terjadi kesalahan saat memproses permintaan Anda. Silakan coba lagi nanti."
        
    async def run(self, query: str) -> Dict[str, Any]:
        """Main method to run the LLM process."""
        response = await self.generate_response(query)
        return {
            "query": query,
            "response": response
        }
        
        
if __name__ == "__main__":
    llm_process = LLMProcess()
    query = "saya mau pengajuan zoom unit apa yg harus sy lakukan? syaratnya apa aja?"
    import asyncio
    response = asyncio.run(llm_process.run(query))
    print(response.get("response", "Tidak ada respons dari LLM.")) 