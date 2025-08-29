# 🤖 Mbot - Assistente Corporativo com IA
O Mbot é um assistente de IA conversacional projetado para otimizar o acesso a informações internas e acelerar processos de consulta as nossas bases de dados(Salesforce, SAP e Conhecimentos internos) para as diversas equipes da empresa incluindo o atendimento e suporte ao cliente.

<img width="1909" height="987" alt="Captura de tela 2025-08-29 184622" src="https://github.com/user-attachments/assets/c3c15a6f-a9cd-476e-b246-84a6ec5023fa" />

# 🎯 Objetivo do Projeto
O objetivo principal do Mbot é servir como um ponto central e inteligente de consulta para dúvidas sobre processos internos e dados de clientes. Ele capacita a equipe a obter respostas rápidas e precisas, diretamente de fontes de dados oficiais como o Salesforce, eliminando a necessidade de navegar por múltiplas telas ou consultar diferentes departamentos.

Para a Equipe: Reduz o tempo de resposta, aumenta a precisão das informações e padroniza o conhecimento.

Para a Empresa: Centraliza o conhecimento, diminui a carga de trabalho em consultas repetitivas e cria uma base para futuras integrações, como a consulta de dados no SAP.

# 🏛️ Arquitetura do Sistema
O projeto é construído em uma arquitetura desacoplada, garantindo escalabilidade, segurança e manutenibilidade.

Front-end (front-end-stream-lit): Uma interface web interativa construída com Streamlit. É responsável por gerenciar a autenticação do usuário(juntamente com o Keycloak), exibir a conversa e comunicar-se com o back-end.

Back-end (back-end-fast-api): O cérebro da aplicação. Uma API RESTful assíncrona construída com FastAPI. Suas responsabilidades incluem validar a identidade do usuário, orquestrar a lógica de IA com LangChain, conectar-se às fontes de dados e persistir o histórico das conversas.

Fontes de Dados:

PostgreSQL: Armazena dados relacionais (usuários, histórico de chats).

Qdrant: Banco de dados vetorial para buscas semânticas em documentos de processos.

Salesforce: Acessado em tempo real para buscar dados de clientes, oportunidades (OPs) e contatos.

# PostgreSQL

<img width="1170" height="762" alt="Captura de tela 2025-08-29 184722" src="https://github.com/user-attachments/assets/936524b5-5b49-485f-83bf-2a41e4e78b6a" />

# Qdrant

<img width="1824" height="844" alt="Captura de tela 2025-08-29 185001" src="https://github.com/user-attachments/assets/12bd5426-9343-438f-bcc0-bf272f95b3a4" />

# FastAPI

<img width="1901" height="951" alt="Captura de tela 2025-08-29 184635" src="https://github.com/user-attachments/assets/3d28d50b-ca13-44ea-8b79-d77da8ece2ad" />

# Autenticação & Infraestrutura

🔑 Keycloak: Solução de gerenciamento de identidade e acesso (IAM).

## 🛠️ Tecnologias Utilizadas

| Categoria           | Tecnologia                             |
| ------------------- | -------------------------------------- |
| **Back-end** | FastAPI, Pydantic, SQLAlchemy, Alembic |
| **IA & Orquestração** | LangChain                              |
| **Front-end** | Streamlit                              |
| **Bancos de Dados** | PostgreSQL, Qdrant (Banco Vetorial)    |
| **Autenticação** | Keycloak (OIDC)                        |
| **Linguagem** | Python 3.10+                           |

## 📋 Pré-requisitos

Antes de começar, certifique-se de que tem os seguintes softwares instalados:

- [Python 3.10+](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/products/docker-desktop/) (Recomendado para correr PostgreSQL, Qdrant e Keycloak)
- Git

## 🚀 Como Executar o Projeto

Siga estes passos para configurar e executar o projeto localmente.

### 1. Clonar o Repositório

```bash
git clone [[https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)](https://github.com/gustavoSilvaAlves/ChatbotAI.git)
cd seu-repositorio

📂 Estrutura do Projeto
.
├── back-end-fast-api/    # Projeto da API com FastAPI
├── front-end-stream-lit/ # Projeto da interface com Streamlit
├── .gitignore            # Ficheiros e pastas a serem ignorados pelo Git
└── README.md             # Este ficheiro


