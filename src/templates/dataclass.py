from pydantic import BaseModel, Field


class RawFlood(BaseModel):
    day: str = Field(..., min_length=10, max_length=10)
    status: str = Field(..., min_length=5, max_length=20)

    periodo: str = Field(..., min_length=5, max_length=20)
    endereco: str = Field(..., min_length=5, max_length=150)
    sentido: str = Field(..., min_length=5, max_length=50)
    referencia: str = Field(..., min_length=5, max_length=150)
