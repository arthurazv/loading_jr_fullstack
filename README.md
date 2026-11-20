# Central de Solicitações

Aplicação full-stack de gerenciamento para criação, consulta, filtragem e atualização de solicitações, construída com FastAPI (Python) no backend e React (Vite) no frontend.

## Stack Tecnológica

- **Backend:** FastAPI, SQLAlchemy, SQLite, Pydantic
- **Frontend:** React, Vite
- **Testes:** pytest

## Funcionalidades e Requisitos Atendidos

- **RF01 — Cadastro:** Permite registrar solicitações com título, descrição, categoria e prioridade (baixa, média ou alta). O status inicial padrão é sempre **Aberta**.
- **RF02 — Consulta:** Listagem completa das solicitações, exibindo detalhes cadastrais e status atualizado.
- **RF03 — Filtros:** Filtragem dinâmica da listagem por status e por nível de prioridade.
- **RF04 — Regra de Negócio (Fluxo de Estados):** Controle estrito da máquina de estados: `Aberta` → `Em andamento` → `Concluída`. O sistema bloqueia transições fora de ordem ou saltos de etapa.
- **RF05 — Persistência:** Armazenamento relacional via SQLite/SQLAlchemy, garantindo a integridade dos dados entre reinicializações da aplicação.
- **RF06 — Integração e Validação:** Interface web totalmente conectada à API REST; validação com retorno claro e amigável para campos obrigatórios vazios e tentativas de transição de status inválidas.

## Como Executar Localmente

### Execução Rápida (Instalador Automático)

Na raiz do projeto, execute o instalador para criar um ambiente virtual temporário, instalar as dependências e iniciar backend e frontend automaticamente:

```bash
python3 installer.py
```

- Interface Web: `http://localhost:5173`
- API / Swagger UI: `http://127.0.0.1:8000/docs`
- Ao pressionar `ENTER` (ou `Ctrl+C`), o script encerra os servidores e remove os arquivos temporários criados.

### Backend (Manual)

1. Crie e ative um ambiente virtual (opcional, mas recomendado):
   
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

2. Instale as dependências:
   
   ```bash
   pip install -r requirements.txt
   ```

3. Inicie a API em modo de desenvolvimento:
   
   ```bash
   uvicorn app.main:app --reload
   ```

A documentação interativa estará disponível em: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (Swagger UI).

### Frontend

1. Instale as dependências:
   
   ```bash
   npm install
   ```

2. Inicie o servidor de desenvolvimento:
   
   ```bash
   npm run dev
   ```

### Testes Automatizados

Para executar a suíte de testes unitários e de integração do backend:

```bash
pytest
```

## Uso de IA

Neste projeto, ferramentas de IA foram utilizadas para geração de código boilerplate, apoio na concepção da arquitetura e aceleração da prototipagem da interface (UI).

**Modelos utilizados:**

- Ornith 1.5 9B
- Google Hydrogen
