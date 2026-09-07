# Surveil the Bulk 👁️💧

Uma API RESTful assíncrona para gerenciar coleções e decks de Magic: The Gathering. 

O sistema consome a API pública do Scryfall, processa cartas (incluindo dupla-face) e gerencia o inventário local usando um banco de dados relacional (SQLite), tudo blindado por tipagem forte e validação de dados.

## 🚀 Tecnologias e Arquitetura

O projeto foi construído utilizando práticas modernas do ecossistema Python (Clean Architecture):

- **[FastAPI](https://fastapi.tiangolo.com/):** Framework web assíncrono de altíssima performance para roteamento.
- **[Pydantic (V2)](https://docs.pydantic.dev/):** Modelagem de entidades, serialização e validação rígida de dados de entrada/saída.
- **[uv](https://github.com/astral-sh/uv):** Gerenciamento ultrarrápido de dependências e ambientes virtuais.
- **SQLite:** Banco de dados relacional embarcado (tabelas normalizadas para relação Carta/Face 1:N).
- **Pytest:** Suíte de testes automatizados E2E simulando requisições e falhas do cliente.
- **Ruff:** Linter e formatter super rápido.

## 🛠️ Como rodar o projeto localmente

### 1. Pré-requisitos
- Python 3.x instalado.
- Instale o `uv` no seu sistema:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

### 2. Rodando a Aplicação
Clone este repositório e navegue até a pasta:
```bash
git clone https://github.com/ArthurSVieira/surveil-the-bulk.git
cd surveil-the-bulk
```

Baixe as dependências e suba o servidor embutido (o banco será inicializado automaticamente):
```bash
uv run uvicorn surveil_the_bulk.app:app --reload
```

## 📖 Documentação Interativa (Swagger)

A grande vantagem de utilizar FastAPI é a geração de documentação automática.
Com o servidor rodando, acesse no seu navegador:

- **Swagger UI (Interativo):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc (Estático):** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

Lá você poderá testar todas as rotas (adicionar cartas, buscar coleção, criar decks) clicando no botão *Try it out*, sem precisar de ferramentas de terceiros como o Postman.

## 🧩 Principais Rotas da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET`  | `/api/cards` | Retorna as cartas da coleção (Filtros: bulk, want, trade) |
| `POST` | `/api/cards` | Adiciona uma nova carta à coleção (busca no Scryfall) |
| `GET`  | `/api/decks` | Lista os decks cadastrados |
| `POST` | `/api/decks` | Cria um deck novo |
| `POST` | `/api/decks/cards` | Adiciona cartas existentes a um deck |
| `GET`  | `/api/deck/cards/{deck}` | Retorna a decklist de um deck específico |

## 🧪 Testes e Qualidade
Para rodar a suíte de testes E2E e o linter, utilize:
```bash
uv run pytest
uv run ruff check
```
