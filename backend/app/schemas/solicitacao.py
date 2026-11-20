from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

from app.models.solicitacao import PrioridadeEnum, StatusEnum


NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class SolicitacaoCreate(BaseModel):
    titulo: NonEmptyStr
    descricao: NonEmptyStr
    categoria: NonEmptyStr
    prioridade: PrioridadeEnum


class SolicitacaoStatusUpdate(BaseModel):
    status: StatusEnum


class SolicitacaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    titulo: str
    descricao: str
    categoria: str
    prioridade: str
    status: str
    created_at: datetime
    updated_at: datetime
