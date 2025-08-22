# 🤖 Mbot - Assistente Corporativo com IA
O Mbot é um assistente de IA conversacional projetado para otimizar o acesso a informações internas e acelerar processos de consulta as nossas bases de dados(Salesforce, SAP e Conhecimentos internos) para equipes de atendimento e suporte ao cliente.

# 🎯 Objetivo do Projeto
O objetivo principal do Mbot é servir como um ponto central e inteligente de consulta para dúvidas sobre processos internos e dados de clientes. Ele capacita a equipe a obter respostas rápidas e precisas, diretamente de fontes de dados oficiais como o Salesforce, eliminando a necessidade de navegar por múltiplas telas ou consultar diferentes departamentos.

Para a Equipe: Reduz o tempo de resposta, aumenta a precisão das informações e padroniza o conhecimento.

Para a Empresa: Centraliza o conhecimento, diminui a carga de trabalho em consultas repetitivas e cria uma base para futuras integrações, como a consulta de dados no SAP.

# 🏛️ Arquitetura do Sistema
O projeto é construído em uma arquitetura desacoplada, garantindo escalabilidade, segurança e manutenibilidade.

Front-end (front-end-stream-lit): Uma interface web interativa construída com Streamlit. É responsável por gerenciar a autenticação do usuário, exibir a conversa e comunicar-se com o back-end.

Back-end (back-end-fast-api): O cérebro da aplicação. Uma API RESTful assíncrona construída com FastAPI. Suas responsabilidades incluem validar a identidade do usuário, orquestrar a lógica de IA com LangChain, conectar-se às fontes de dados e persistir o histórico das conversas.

Fontes de Dados:

PostgreSQL: Armazena dados relacionais (usuários, histórico de chats).

Qdrant: Banco de dados vetorial para buscas semânticas em documentos de processos.

Salesforce: Acessado em tempo real para buscar dados de clientes, oportunidades (OPs) e contatos.

# 🛠️ Tecnologias Utilizadas
Categoria

Tecnologia

Back-end

FastAPI, LangChain, Pydantic, SQLAlchemy, Alembic

Front-end

Streamlit

Bancos de Dados

PostgreSQL, Qdrant (Banco Vetorial)

Autenticação

Keycloak (OIDC)

Linguagem

Python 3.10+

# 🚀 Como Executar o Projeto
Siga os passos abaixo para configurar e rodar o ambiente de desenvolvimento local.

Pré-requisitos
Python 3.10+

Git

Docker (recomendado para rodar os serviços de BD e Keycloak)

1. Configuração do Back-end
# Navegue até a pasta do back-end
cd back-end-fast-api

# Crie e ative um ambiente virtual (exemplo para Windows)
python -m venv .venv
.\.venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Crie e configure seu arquivo .env a partir do .env.example

# Rode o servidor da API
uvicorn api.main:app --reload

O servidor estará rodando em http://localhost:8000.

2. Configuração do Front-end
# Em um NOVO terminal, navegue até a pasta do front-end
cd front-end-stream-lit

# Crie e ative um ambiente virtual (mesmos passos do back-end)
python -m venv .venv
.\.venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Crie e configure seu arquivo .env

# Rode a aplicação Streamlit
streamlit run main.py

A aplicação estará acessível em http://localhost:8501 (ou na porta que você configurar).
