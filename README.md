# 🤖 Mbot - Assistente Corporativo com IA
![Python](https://img.shields.io/badge/Python-3.11-blue.svg) ![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-green.svg) ![LangChain](https://img.shields.io/badge/LangChain-blue?logo=langchain) ![LangGraph](https://img.shields.io/badge/LangGraph-orange?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxZW0iIGhlaWdodD0iMWVtIiB2aWV3Qm94PSIwIDAgMjQgMjQiPjxwYXRoIGZpbGw9IiNmZmYiIGQ9Ik00IDdoMnYxMEg0em0zIDBoMnYxMEg3em0zIDBoMnYxMEgxMHptMyAwaDJ2MTBIMTN6bTggMi42OThsLTIuNzk4IDIuNzk3bC0xLjQxNC0xLjQxNEwxOC4xNzIgMTBMMTYuNTggOC40MTNsMS40MTQtMS40MTRaTTIgN2gxNHYxMEgyek0xIDV2MTRoMTZWNWEyIDIgMCAwIDAtMi0ySDNBMiAyIDAgMCAwIDEgNSIvPjwvc3ZnPg==) ![Keycloak](https://img.shields.io/badge/Keycloak-2F81B7.svg?logo=keycloak) ![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker) ![License](https://img.shields.io/badge/License-All%20Rights%20Reserved-red.svg)

O Mbot é um assistente de IA conversacional projetado para otimizar o acesso a informações internas e acelerar processos de consulta as nossas bases de dados(Salesforce, SAP e Conhecimentos internos) para as diversas equipes da empresa incluindo o atendimento e suporte ao cliente.

# 🎯 Objetivo do Projeto
O objetivo principal do Mbot é servir como um ponto central e inteligente de consulta para dúvidas sobre processos internos e dados de clientes. Ele capacita a equipe a obter respostas rápidas e precisas, diretamente de fontes de dados oficiais como o Salesforce, eliminando a necessidade de navegar por múltiplas telas ou consultar diferentes departamentos.

Para a Equipe: Reduz o tempo de resposta, aumenta a precisão das informações e padroniza o conhecimento.

Para a Empresa: Centraliza o conhecimento, diminui a carga de trabalho em consultas repetitivas e cria uma base para futuras integrações, como a consulta de dados no SAP.

# 🏛️ Arquitetura do Sistema
O projeto é construído em uma arquitetura desacoplada, garantindo escalabilidade, segurança e manutenibilidade.

Front-end (front-end-stream-lit): Uma interface web interativa construída com Streamlit. É responsável por gerenciar a autenticação do usuário(juntamente com o Keycloak), exibir a conversa e comunicar-se com o back-end.

Back-end (back-end-fast-api): O cérebro da aplicação. Uma API RESTful assíncrona construída com FastAPI. Suas responsabilidades incluem validar a identidade do usuário, orquestrar a lógica de IA com LangChain, conectar-se às fontes de dados e persistir o histórico das conversas.

###Fontes de Dados:

PostgreSQL: Armazena dados relacionais (usuários, histórico de chats).

Qdrant: Banco de dados vetorial para buscas semânticas em documentos de processos.

Salesforce: Acessado em tempo real para buscar dados de clientes, oportunidades (OPs) e contatos.

# 🛠️ Tecnologias Utilizadas

| Categoria           | Tecnologia                             |
| ------------------- | -------------------------------------- |
| **Back-end** | FastAPI, Pydantic, SQLAlchemy, Alembic |
| **IA & Orquestração** | LangChain                              |
| **Front-end** | Streamlit                              |
| **Bancos de Dados** | PostgreSQL, Qdrant (Banco Vetorial)    |
| **Autenticação** | Keycloak (OIDC)                        |
| **Linguagem** | Python 3.10+                           |
| **Containerização** | Docker, Docker Compose                 |



# 🚀 Como Executar o Projeto (Docker)

A forma mais simples e recomendada de executar este projeto é através do Docker Compose, que orquestra todos os serviços necessários.

### 📋 Pré-requisitos
- [Docker & Docker Compose](https://www.docker.com/products/docker-desktop/)
- [Git](https://git-scm.com/downloads)
- Uma instância do Keycloak, PostgreSQL e Qdrant a correr e acessível pela sua máquina.

### Passos de Execução

1.  **Clonar o Repositório**
    ```bash
    git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
    cd seu-repositorio
    ```

2.  **Configurar os Ficheiros de Ambiente**
    Crie os ficheiros `.env` locais a partir dos exemplos fornecidos.

    ```bash
    # Para o Back-end
    cp back-end-fast-api/.env.example back-end-fast-api/.env

    # Para o Front-end
    cp front-end-stream-lit/.env.example front-end-stream-lit/.env
    ```
    **Importante:** Edite os dois ficheiros `.env` recém-criados com as suas chaves de API, credenciais do banco de dados e configurações do Keycloak.

3.  **Iniciar a Aplicação com Docker Compose**
    Este comando irá construir as imagens do front-end e do back-end e iniciar os contentores.

    ```bash
    docker-compose up --build
    ```
    - A aplicação front-end estará disponível em `http://localhost:8501`.
    - A API do back-end estará disponível em `http://localhost:8000`.

# 🔑 Configuração do Keycloak

Para que a autenticação funcione, o seu realm no Keycloak precisa de ter dois "Clients" configurados: um para o front-end e um para o back-end.

1.  **Cliente do Front-end (`streamlit-frontend`)**
    - **Client ID:** `streamlit-frontend`
    - **Client authentication:** `Off` (cliente público)
    - **Valid Redirect URIs:** `http://localhost:8501/*` (essencial para o redirecionamento após o login)

2.  **Cliente do Back-end (`api-backend-client`)**
    - **Client ID:** `api-backend-client`
    - **Client authentication:** `On`
    - **Service accounts roles:** `On`
    - **Authorization:** `On`

Certifique-se de que as variáveis `KEYCLOAK_BASE_URL`, `KEYCLOAK_REALM`, e `KEYCLOAK_CLIENT_ID` nos seus ficheiros `.env` correspondem exatamente a estas configurações.

# 📂 Estrutura do Projeto
```text
.
├── back-end-fast-api/    # Projeto da API com FastAPI e o seu Dockerfile
├── front-end-stream-lit/ # Projeto da interface com Streamlit e o seu Dockerfile
├── docker-compose.yml    # Orquestra a execução dos dois serviços
├── .gitignore            # Ficheiros e pastas a serem ignorados pelo Git
└── README.md             # Este ficheiro

```


