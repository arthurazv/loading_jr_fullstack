from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def test_session_factory(tmp_path: Path) -> sessionmaker:
    """Create an isolated SQLite database per test."""
    db_file = tmp_path / "test_solicitacoes.db"
    engine = create_engine(
        f"sqlite:///{db_file}", connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    try:
        yield TestingSessionLocal
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(test_session_factory: sessionmaker) -> Generator[TestClient, None, None]:
    """FastAPI TestClient wired to the isolated test database."""

    def override_get_db() -> Generator[Session, None, None]:
        db = test_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_solicitacao_rf01(client: TestClient) -> None:
    payload = {
        "titulo": "  Erro no login  ",
        "descricao": "Usuário não consegue autenticar no portal.",
        "categoria": "Acesso",
        "prioridade": "alta",
    }
    response = client.post("/solicitacoes", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] >= 1
    assert data["titulo"] == "Erro no login"
    assert data["descricao"] == payload["descricao"]
    assert data["categoria"] == "Acesso"
    assert data["prioridade"] == "alta"
    assert data["status"] == "Aberta"


def test_get_solicitacao_detail_and_not_found_rf02(client: TestClient) -> None:
    created = client.post(
        "/solicitacoes",
        json={
            "titulo": "Solicitar monitor",
            "descricao": "Segundo monitor para estação de trabalho.",
            "categoria": "Infraestrutura",
            "prioridade": "média",
        },
    ).json()

    detail_resp = client.get(f"/solicitacoes/{created['id']}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["titulo"] == "Solicitar monitor"

    missing_resp = client.get("/solicitacoes/99999")
    assert missing_resp.status_code == 404


def test_list_and_filter_rf02_rf03(client: TestClient) -> None:
    s1 = client.post(
        "/solicitacoes",
        json={
            "titulo": "Bug no relatório",
            "descricao": "Exportação CSV falha.",
            "categoria": "Sistema",
            "prioridade": "alta",
        },
    ).json()
    s2 = client.post(
        "/solicitacoes",
        json={
            "titulo": "Trocar mouse",
            "descricao": "Botão esquerdo falhando.",
            "categoria": "Hardware",
            "prioridade": "baixa",
        },
    ).json()

    # Avança s1 para Em andamento para testar filtro combinado
    client.patch(f"/solicitacoes/{s1['id']}/status", json={"status": "Em andamento"})

    all_items = client.get("/solicitacoes").json()
    assert len(all_items) == 2

    by_status = client.get("/solicitacoes", params={"status": "Em andamento"}).json()
    assert len(by_status) == 1
    assert by_status[0]["id"] == s1["id"]

    by_priority = client.get("/solicitacoes", params={"prioridade": "baixa"}).json()
    assert len(by_priority) == 1
    assert by_priority[0]["id"] == s2["id"]

    combined = client.get(
        "/solicitacoes", params={"status": "Aberta", "prioridade": "alta"}
    ).json()
    assert combined == []


def test_valid_transitions_rf04(client: TestClient) -> None:
    created = client.post(
        "/solicitacoes",
        json={
            "titulo": "Configurar VPN",
            "descricao": "Acesso remoto para novo colaborador.",
            "categoria": "Redes",
            "prioridade": "média",
        },
    ).json()

    step1 = client.patch(
        f"/solicitacoes/{created['id']}/status", json={"status": "Em andamento"}
    )
    assert step1.status_code == 200
    assert step1.json()["status"] == "Em andamento"

    step2 = client.patch(
        f"/solicitacoes/{created['id']}/status", json={"status": "Concluída"}
    )
    assert step2.status_code == 200
    assert step2.json()["status"] == "Concluída"


def test_invalid_transitions_rf04(client: TestClient) -> None:
    created = client.post(
        "/solicitacoes",
        json={
            "titulo": "Atualizar certificado",
            "descricao": "Certificado SSL expira na próxima semana.",
            "categoria": "Segurança",
            "prioridade": "alta",
        },
    ).json()

    # Não pode pular Aberta -> Concluída
    skip_resp = client.patch(
        f"/solicitacoes/{created['id']}/status", json={"status": "Concluída"}
    )
    assert skip_resp.status_code == 400
    assert "Transição inválida" in skip_resp.json()["detail"]

    # Avança para Em andamento e tenta voltar para Aberta
    client.patch(
        f"/solicitacoes/{created['id']}/status", json={"status": "Em andamento"}
    )
    back_resp = client.patch(
        f"/solicitacoes/{created['id']}/status", json={"status": "Aberta"}
    )
    assert back_resp.status_code == 400

    # Conclui e tenta alterar novamente
    client.patch(f"/solicitacoes/{created['id']}/status", json={"status": "Concluída"})
    after_done_resp = client.patch(
        f"/solicitacoes/{created['id']}/status", json={"status": "Em andamento"}
    )
    assert after_done_resp.status_code == 400


def test_persistence_across_sessions_rf05(
    client: TestClient, test_session_factory: sessionmaker
) -> None:
    created = client.post(
        "/solicitacoes",
        json={
            "titulo": "Backup semanal",
            "descricao": "Verificar rotina de backup no servidor.",
            "categoria": "Infraestrutura",
            "prioridade": "baixa",
        },
    ).json()

    # Simula nova sessão/reinicialização consultando o mesmo arquivo SQLite
    with test_session_factory() as fresh_db:
        from app.models.solicitacao import Solicitacao

        persisted = fresh_db.get(Solicitacao, created["id"])
        assert persisted is not None
        assert persisted.titulo == "Backup semanal"
        assert persisted.status == "Aberta"


@pytest.mark.parametrize(
    "bad_payload",
    [
        {
            "titulo": "   ",
            "descricao": "Descrição válida",
            "categoria": "TI",
            "prioridade": "alta",
        },
        {
            "titulo": "Título válido",
            "descricao": "",
            "categoria": "TI",
            "prioridade": "média",
        },
        {
            "titulo": "Título válido",
            "descricao": "Descrição válida",
            "categoria": "   ",
            "prioridade": "baixa",
        },
        {
            "titulo": "Título válido",
            "descricao": "Descrição válida",
            "categoria": "TI",
            "prioridade": "urgente",
        },
    ],
)
def test_reject_blank_fields_and_invalid_priority_rf06(
    client: TestClient, bad_payload: dict[str, str]
) -> None:
    response = client.post("/solicitacoes", json=bad_payload)
    assert response.status_code == 422


def test_delete_solicitacao(client: TestClient) -> None:
    created = client.post(
        "/solicitacoes",
        json={
            "titulo": "Solicitação temporária",
            "descricao": "Será removida via DELETE.",
            "categoria": "Teste",
            "prioridade": "baixa",
        },
    ).json()

    del_resp = client.delete(f"/solicitacoes/{created['id']}")
    assert del_resp.status_code == 204

    get_resp = client.get(f"/solicitacoes/{created['id']}")
    assert get_resp.status_code == 404

    missing_del = client.delete(f"/solicitacoes/{created['id']}")
    assert missing_del.status_code == 404


def test_search_by_name(client: TestClient) -> None:
    client.post(
        "/solicitacoes",
        json={
            "titulo": "Trocar mouse sem fio",
            "descricao": "Mouse parou de responder.",
            "categoria": "Hardware",
            "prioridade": "baixa",
        },
    )
    client.post(
        "/solicitacoes",
        json={
            "titulo": "Conferir estoque",
            "descricao": "Contagem semanal.",
            "categoria": "Estoque",
            "prioridade": "média",
        },
    )

    resp = client.get("/solicitacoes", params={"busca": "MOUSE"})
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["titulo"] == "Trocar mouse sem fio"
