from agno.models.groq import Groq
from agno.agent import Agent
import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import pandas as pd


load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")


class ExcelAnalysisSchema(BaseModel):
    answer: str = Field(..., description="Output hasil analisis Excel")


class ExcelAutomosAgent:
    def __init__(self):
        self._init_agent()

    def _init_agent(self):
        self.agent = Agent(
            name="Excel Automos Agent",
            role="AI agent untuk membersihkan & menganalisis data Excel dengan batas token kecil.",
            model=Groq(
                id="meta-llama/llama-4-scout-17b-16e-instruct",
                api_key=API_KEY
            ),
            instructions=[
                "Analisis hanya berdasarkan ringkasan data yang diberikan.",
                "Jangan meminta seluruh dataset.",
                "Berikan insight yang akurat dari metadata, statistik, dan sample row."
            ],
            output_schema=ExcelAnalysisSchema,
            use_json_mode=True
        )

    def _read_excel(self, excel_path: str) -> pd.DataFrame:
        df = pd.read_excel(excel_path)
        return df

    def _summarize_df(self, df: pd.DataFrame) -> dict:
        summary = {
            "columns": list(df.columns),
            "dtypes": {col: str(df[col].dtype) for col in df.columns},
            "missing_values": df.isna().sum().to_dict(),
            "describe": df.describe(include="all").to_dict(),
            "sample_head": df.head(10).to_dict(orient="records"),
            "sample_tail": df.tail(10).to_dict(orient="records"),
            "total_rows": len(df)
        }
        return summary

    def analyze(self, excel_path: str, instruction: str):
        df = self._read_excel(excel_path)

        summary = self._summarize_df(df)

        prompt = f"""
Berikut ringkasan dataset Excel:

{json.dumps(summary, indent=2)}

Instruksi pengguna: {instruction}

Gunakan ringkasan ini untuk memberikan insight yang akurat.
Jangan minta data tambahan.
"""
        result = self.agent.run(prompt)
        return result.content.model_dump()


if __name__ == "__main__":
    agent = ExcelAutomosAgent()

    excel_file = "data/LayananeService.xlsx"
    instruction = "Berikan analisis insight penting dari dataset ini"

    result = agent.analyze(excel_file, instruction)
    print(json.dumps(result, indent=2))
