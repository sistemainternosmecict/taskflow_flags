# Módulo de Gestão de Flags de Atendimento 🚩

Este módulo é um componente interno projetado para estender o sistema de gestão de demandas existente no setor. Ele permite o controle refinado do status de atendimento das tarefas de forma desacoplada, utilizando um banco de dados MySQL local com persistência gerenciada via SQLAlchemy, fornecendo as informações necessárias para renderizar indicadores visuais no Frontend com base no ID de cada tarefa.

---

> [!WARNING]
> ### ⚠️ BREAKING CHANGE: Migração de Supabase para MySQL Local (SQLAlchemy)
> O serviço e a biblioteca do Supabase foram completamente descontinuados e removidos do projeto. A persistência de dados agora é realizada diretamente em banco de dados **MySQL local** utilizando **SQLAlchemy** e **PyMySQL**.
> - **Variáveis descontinuadas:** `FLAG_SUPABASE_URL` e `FLAG_SUPABASE_KEY`.
> - **Nova variável obrigatória:** `LOCAL_DB_URL` (formato `mysql+pymysql://<user>:<password>@<host>:<port>/<database>?charset=utf8mb4`).
> - **Tabela utilizada:** `tb_flags_register`.

---

## 🛠️ Tecnologias Utilizadas

* **Python 3.13+**
* **FastAPI** (Construção das rotas e API HTTP)
* **SQLAlchemy** (ORM e gerenciamento de sessões do banco de dados)
* **PyMySQL** (Driver de conexão MySQL)
* **Pydantic** (Validação de dados e Schemas/DTOs)
* **Pytest** & **pytest-cov** (Testes automatizados unitários e de integração com cobertura)

---

## 📐 Arquitetura e Estrutura de Pastas

O projeto adota uma arquitetura limpa em camadas para isolar completamente as responsabilidades de negócio da infraestrutura de banco de dados e rotas HTTP.

```text
📂 taskflow_flags
 ┃
 ┣ 📂 domain           # Schemas Pydantic, DTOs e Enums de Status
 ┣ 📂 routers          # Rotas HTTP e Endpoints (FastAPI)
 ┣ 📂 service          # Camada de Regras de Negócio e Transições de Status
 ┣ 📂 repository       # Integração e Persistência de dados (SQLAlchemy / MySQL)
 ┗ 📂 tests            # Testes Unitários e de Integração (Pytest)
```

---

## 🎨 Mapeamento de Status (Flags)

O frontend consome os dados deste módulo para renderizar indicadores visuais baseados no `task_id`. As opções são definidas no Enum `FlagStatusEnum`:

| Status | Descrição / Regra de Negócio |
| --- | --- |
| `ENTREGA_PARCIAL` | A tarefa recebeu atendimento, mas faltam itens na entrega. |
| `DEVOLUCAO_EQUIPAMENTO` | Processo de devolução de equipamento em andamento. |
| `AGUARDANDO_ESTOQUE` | Aguardando disponibilidade de itens no estoque. |
| `RETIFICACAO_OFICIO` | Depende de retificação em documentação oficial/ofício. |

---

## 🚀 Como Executar o Projeto

### 1. Clonar o repositório e acessar a pasta

```bash
git clone https://github.com/sistemainternosmecict/taskflow_flags.git
cd taskflow_flags
```

### 2. Configurar o ambiente virtual e dependências

```bash
uv sync
```

### 3. Variáveis de Ambiente (`.env`)

Crie um arquivo `.env` na raiz do projeto configurando a URL do MySQL local:

```env
LOCAL_DB_URL=mysql+pymysql://thyez:sistec2024@127.0.0.1:3306/smecict_2026?charset=utf8mb4
CORS_ORIGINS=http://192.168.100.215:8081,http://192.168.100.215,https://taskflow-frontend-pqok.onrender.com
```

### 4. Iniciar o Servidor

```bash
uv run uvicorn main:app --reload
```

A documentação interativa e auto-gerada da API estará disponível em: `http://127.0.0.1:8000/docs`

---

## 🧪 Testes Automatizados (Pytest)

O projeto possui uma suíte completa de testes:
- **Testes Unitários:** Executam de forma isolada com mocks da camada de banco de dados (`tests/unit/`).
- **Testes de Integração:** Validam operações reais de CRUD diretamente contra o banco MySQL local (`tests/integration/`).

Para rodar toda a suíte de testes com relatório de cobertura:

```bash
chmod +x pipeline.sh
./pipeline.sh
```

---

## 🔗 Endpoints da API

### `POST /api/v1/flag/init`
* **Descrição:** Inicializa o registro de uma nova flag na tabela `tb_flags_register` vinculada a um `task_id`.
* **Payload:** `CreateFlag` (`tb_flags_task_id`, `tb_flags_task_user_id`)
* **Resposta:** `FlagResponse`

### `GET /api/v1/flag/{task_id}`
* **Descrição:** Retorna as informações e o status atual da flag vinculada ao `task_id`.
* **Resposta:** `FlagResponse`

### `GET /api/v1/flag`
* **Descrição:** Retorna a listagem completa de todas as flags registradas.
* **Resposta:** `list[FlagResponse]`

### `POST /api/v1/flag/batch`
* **Descrição:** Retorna as flags correspondentes a uma lista de IDs de tarefas.
* **Payload:** `TaskBatchRequest` (`task_ids: list[str]`)
* **Resposta:** `list[FlagResponse]`

### `PUT /api/v1/flag`
* **Descrição:** Atualiza o status da flag vinculada à tarefa.
* **Payload:** `UpdateFlagStatus` (`tb_flags_task_id`, `tb_flags_status`)
* **Resposta:** `UpdateFlagResponse`

### `DELETE /api/v1/flag/{task_id}`
* **Descrição:** Remove o registro da flag do banco de dados para a tarefa indicada por `task_id`.
* **Resposta:** `FlagResponse`

---

## 📄 Licença

Este projeto é de uso interno do setor e não possui licença de distribuição pública.
