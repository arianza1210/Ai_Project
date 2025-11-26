from pydantic import BaseModel, Field


class ListSaham(BaseModel):
    symbols: list[str] = Field(..., description="Daftar simbol saham")