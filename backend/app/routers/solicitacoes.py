from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.solicitacao import PrioridadeEnum, StatusEnum
from app.schemas.solicitacao import (
    SolicitacaoCreate,
    SolicitacaoResponse,
    SolicitacaoStatusUpdate,
)
from app.services.solicitacao_service import (
    create_solicitacao,
    delete_solicitacao,
    get_solicitacao_by_id,
    list_solicitacoes,
    update_solicitacao_status,
)

router = APIRouter(prefix="/solicitacoes", tags=["Solicitações"])


@router.post("", response_model=SolicitacaoResponse, status_code=status.HTTP_201_CREATED)
def criar_solicitacao(
    payload: SolicitacaoCreate, db: Session = Depends(get_db)
) -> SolicitacaoResponse:
    db_solicitacao = create_solicitacao(db, payload)
    return db_solicitacao


@router.get("", response_model=list[SolicitacaoResponse])
def listar_solicitacoes(
    status: StatusEnum | None = Query(default=None),
    prioridade: PrioridadeEnum | None = Query(default=None),
    busca: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[SolicitacaoResponse]:
    db_solicitacoes = list_solicitacoes(db, status, prioridade, busca)
    return db_solicitacoes


@router.get("/{solicitacao_id}", response_model=SolicitacaoResponse)
def obter_solicitacao(
    solicitacao_id: int, db: Session = Depends(get_db)
) -> SolicitacaoResponse:
    db_solicitacao = get_solicitacao_by_id(db, solicitacao_id)
    return db_solicitacao


@router.patch("/{solicitacao_id}/status", response_model=SolicitacaoResponse)
def alterar_status(
    solicitacao_id: int,
    payload: SolicitacaoStatusUpdate,
    db: Session = Depends(get_db),
) -> SolicitacaoResponse:
    db_solicitacao = update_solicitacao_status(db, solicitacao_id, payload.status)
    return db_solicitacao


@router.delete("/{solicitacao_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_solicitacao(solicitacao_id: int, db: Session = Depends(get_db)) -> None:
    delete_solicitacao(db, solicitacao_id)
