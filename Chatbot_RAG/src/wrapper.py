import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional
from groq import Groq
from ragas.llms import LangchainLLMWrapper
from langchain.llms.base import LLM as LangchainLLM

# Load .env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class GrokLangchainLLM(LangchainLLM):
    api_key: Optional[str] = None
    model: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    temperature: float = 0.0
    client: Optional[Groq] = None

    class Config:
        arbitrary_types_allowed = True

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "meta-llama/llama-4-scout-17b-16e-instruct",
        temperature: float = 0.0
    ):
        super().__init__()
        object.__setattr__(self, "api_key", api_key or os.getenv("GROK_API_KEY"))
        object.__setattr__(self, "model", model)
        object.__setattr__(self, "temperature", temperature)
        object.__setattr__(self, "client", Groq(api_key=self.api_key))

    def _call(self, prompt: str, stop=None, run_manager=None, **kwargs):
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1028,
            temperature=self.temperature
        )
        return completion.choices[0].message.content
    
    async def _acall(self, prompt: str, stop=None, run_manager=None, **kwargs):
        return self._call(prompt, stop=stop, run_manager=run_manager, **kwargs)


    @property
    def _identifying_params(self):
        return {"model": self.model, "temperature": self.temperature}

    @property
    def _llm_type(self):
        return "grok"

# Pemakaian di RAGAS
grok_llm = GrokLangchainLLM(model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0.7)
llm_wrapper = LangchainLLMWrapper(grok_llm)

# print(grok_llm("Halo Grok, kenalkan dirimu"))
