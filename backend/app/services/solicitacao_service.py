from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.solicitacao import PrioridadeEnum, StatusEnum, Solicitacao
from app.schemas.solicitacao import SolicitacaoCreate


ALLOWED_TRANSITIONS: dict[StatusEnum, list[StatusEnum]] = {
    StatusEnum.ABERTA: [StatusEnum.EM_ANDAMENTO],
    StatusEnum.EM_ANDAMENTO: [StatusEnum.CONCLUIDA],
    StatusEnum.CONCLUIDA: [],
}


def create_solicitacao(db: Session, payload: SolicitacaoCreate) -> Solicitacao:
    db_solicitacao = Solicitacao(
        titulo=payload.titulo,
        descricao=payload.descricao,
        categoria=payload.categoria,
        prioridade=payload.prioridade.value,
        status=StatusEnum.ABERTA.value,
    )
    db.add(db_solicitacao)
    db.commit()
    db.refresh(db_solicitacao)
    return db_solicitacao


def list_solicitacoes(
    db: Session,
    status: StatusEnum | None = None,
    prioridade: PrioridadeEnum | None = None,
    busca: str | None = None,
) -> list[Solicitacao]:
    query = db.query(Solicitacao)
    if status is not None:
        query = query.filter(Solicitacao.status == status.value)
    if prioridade is not None:
        query = query.filter(Solicitacao.prioridade == prioridade.value)
    if busca is not None and busca.strip():
        query = query.filter(Solicitacao.titulo.ilike(f"%{busca.strip()}%"))
    return query.order_by(Solicitacao.id.desc()).all()


def get_solicitacao_by_id(db: Session, solicitacao_id: int) -> Solicitacao:
    db_solicitacao = db.get(Solicitacao, solicitacao_id)
    if db_solicitacao is None:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada.")
    return db_solicitacao


def update_solicitacao_status(
    db: Session,
    solicitacao_id: int,
    new_status: StatusEnum,
) -> Solicitacao:
    db_solicitacao = db.get(Solicitacao, solicitacao_id)
    if db_solicitacao is None:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada.")

    current_status = StatusEnum(db_solicitacao.status)
    allowed_transitions = ALLOWED_TRANSITIONS[current_status]
    if new_status not in allowed_transitions:
        raise HTTPException(
            status_code=400,
            detail=f"Transição inválida: não é permitido alterar de '{db_solicitacao.status}' para '{new_status.value}'.",
        )

    db_solicitacao.status = new_status.value
    db.commit()
    db.refresh(db_solicitacao)
    return db_solicitacao


def delete_solicitacao(db: Session, solicitacao_id: int) -> None:
    db_solicitacao = get_solicitacao_by_id(db, solicitacao_id)
    db.delete(db_solicitacao)
    db.commit()
