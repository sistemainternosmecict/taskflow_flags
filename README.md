# Módulo de Gestão de Flags de Atendimento 🚩

Este módulo é um componente interno projetado para estender o sistema de gestão de demandas existente no setor. Ele permite o controle refinado do status de atendimento das tarefas (como entregas parciais ou prontas para revisão) de forma desacoplada, utilizando o Supabase como banco de dados auxiliar e fornecendo as informações necessárias para renderizar indicadores visuais (bolinhas coloridas) no Frontend com base no ID de cada tarefa.

---

## 🛠️ Tecnologias Utilizadas

* **Python 3.11+**
* **FastAPI** (Construção das rotas e API)
* **Pydantic** (Validação de dados e Schemas/DTOs)
* **Supabase Python Client** (Persistência de dados)
* **Pytest** (Testes automatizados e TDD)
---

## 📐 Arquitetura e Estrutura de Pastas

O projeto adota uma arquitetura limpa em camadas para isolar completamente as responsabilidades de negócio da infraestrutura de banco de dados e rotas HTTP.

```text
📂 taskflow_flags
 ┃
 ┣ 📂 domain           # Schemas Pydantic, DTOs e Contratos de Dados
 ┣ 📂 routers             # Rotas HTTP e Endpoints (FastAPI)
 ┣ 📂 service          # Camada de Regras de Negócio e Transições de Status
 ┣ 📂 repository       # Integração e Persistência de dados (Supabase)
 ┗ 📂 tests                  # Testes Unitários e de Integração (Pytest)
```

---

## 🎨 Mapeamento de Status (Flags)

O frontend consome os dados deste módulo para renderizar indicadores visuais baseados no `task_id`. As cores e comportamentos são definidos conforme o Enum `flag_status_enum`:

| Status | Cor no Front | Descrição / Regra de Negócio |
| --- | --- | --- |
| `ENTREGA_PARCIAL` | 🟠 Laranja | A tarefa recebeu atendimento, mas faltam itens na lista. |
| `AGUARDANDO_EMPRESA` | 🔵 Azul | Aguardando retorno de fornecedor ou empresa externa. |
| `FALTA_EQUIPAMENTO` | 🔴 Vermelho | Impedimento crítico por falta de estoque ou insumos. |
| `PRONTO_PARA_REVISAO` | 🟢 Verde | Atendimento 100% concluído. Gatilho para avanço de etapa. |
| `AGUARDANDO_OFICIO` | 🟣 Roxo | Depende de documentação oficial para receber anexo de relatório. |

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

Crie um arquivo `.env` na raiz do projeto com as credenciais de acesso ao Supabase:

```env
FLAG_SUPABASE_URL=https://sua-url-do-supabase.supabase.co
FLAG_SUPABASE_KEY=sua-chave-api-anon-ou-service-role
```

### 4. Iniciar o Servidor

```bash
uv run uvicorn main:app --reload
```

A documentação interativa e auto-gerada da API estará disponível em: `http://127.0.0.1:8000/docs`

---

## 🧪 Testes Automatizados (Pytest)

O desenvolvimento deste módulo priorizou a abordagem *Bottom-Up*, onde as camadas de validação (`domain_layer`) e banco de dados (`repository_layer`) foram criadas e testadas diretamente através do Pytest antes mesmo da criação das rotas HTTP, garantindo robustez na persistência.

Para rodar a suíte de testes locais, com testes de unidade e testes de integração, exibindo a cobertura:

```bash
chmod +x pipeline.sh
./pipeline.sh
```

---

## 🔗 Endpoints da API

### `POST /api/v1/flag/init`
* **Descrição:** Inicializa o registro de uma nova flag na tabela `tb_flags_register` vinculada a um `task_id` existente.
* **Payload:** `CreateFlag`
### `GET /api/v1/flag/{task_id}`
* **Descrição:** Retorna as informações e o status atual da flag para que o Frontend renderize a bolinha correspondente.
* **Resposta:** `FlagResponse`
### `GET /api/v1/flag`
* **Descrição:** Retorna as informações e o status atual de todas as flags iniciadas.
* **Resposta:** `list[FlagResponse]`
### `PUT /api/v1/flag/{task_id}`
* **Descrição:** Acionado pelo botão de ação na interface. Atualiza o status da flag (ex: altera de `ENTREGA_PARCIAL` para `PRONTO_PARA_REVISAO`).
* **Payload:** `UpdateFlagStatus`
### `DELETE /api/v1/flag/{task_id}`
* **Descrição:** Remove o registro da flag do banco de dados para a tarefa indicada por `task_id`.
* **Resposta:** `FlagResponse`
---

## 📄 Licença


Este projeto é de uso interno do setor e não possui licença de distribuição pública.
