from enum import Enum
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database import Base


class PrioridadeEnum(str, Enum):
    BAIXA = "baixa"
    MEDIA = "média"
    ALTA = "alta"


class StatusEnum(str, Enum):
    ABERTA = "Aberta"
    EM_ANDAMENTO = "Em andamento"
    CONCLUIDA = "Concluída"


class Solicitacao(Base):
    __tablename__ = "solicitacoes"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(150), nullable=False)
    descricao = Column(Text, nullable=False)
    categoria = Column(String(80), nullable=False)
    prioridade = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default=StatusEnum.ABERTA.value)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
