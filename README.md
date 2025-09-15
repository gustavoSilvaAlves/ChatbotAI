# 🤖 Mbot - Assistente Corporativo com IA
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-%2300867B?style=for-the-badge)
![LangGraph](https://img.shields.io/badge/LangGraph-%23239083?style=for-the-badge)
![Qdrant](https://img.shields.io/badge/Qdrant-DC2C04?style=for-the-badge)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-9A0000?style=for-the-badge)
![Keycloak](https://img.shields.io/badge/Keycloak-00B8D4?style=for-the-badge&logo=keycloak&logoColor=white)

O Mbot é um assistente de IA conversacional projetado para otimizar o acesso a informações internas e acelerar processos de consulta as nossas bases de dados(Salesforce, SAP e Conhecimentos internos) para as diversas equipes da empresa incluindo o atendimento e suporte ao cliente.

<img width="1907" height="954" alt="Captura de tela 2025-09-15 201206" src="https://github.com/user-attachments/assets/5ea1acca-91dc-41d5-983b-edc8d46e7206" />
<img width="1904" height="948" alt="Captura de tela 2025-09-15 201252" src="https://github.com/user-attachments/assets/771b24b8-d89c-4d88-b170-2bbb1a367d36" />

# 🎯 Objetivo do Projeto
O objetivo principal do Mbot é servir como um ponto central e inteligente de consulta para dúvidas sobre processos internos e dados de clientes. Ele capacita a equipe a obter respostas rápidas e precisas, diretamente de fontes de dados oficiais como o Salesforce, eliminando a necessidade de navegar por múltiplas telas ou consultar diferentes departamentos.

Para a Equipe: Reduz o tempo de resposta, aumenta a precisão das informações e padroniza o conhecimento.

Para a Empresa: Centraliza o conhecimento, diminui a carga de trabalho em consultas repetitivas e cria uma base para futuras integrações, como a consulta de dados no SAP.

# 🏛️ Arquitetura do Sistema
O projeto é construído em uma arquitetura desacoplada, garantindo escalabilidade, segurança e manutenibilidade.

Front-end (front-end-stream-lit): Uma interface web interativa construída com Streamlit. É responsável por gerenciar a autenticação do usuário(juntamente com o Keycloak), exibir a conversa e comunicar-se com o back-end.

Back-end (back-end-fast-api): O cérebro da aplicação. Uma API RESTful assíncrona construída com FastAPI. Suas responsabilidades incluem validar a identidade do usuário, orquestrar a lógica de IA com LangChain, conectar-se às fontes de dados e persistir o histórico das conversas.

Fontes de Dados:

# PostgreSQL:

Armazena dados relacionais (usuários, histórico de chats).

<img width="1168" height="729" alt="Captura de tela 2025-09-15 201350" src="https://github.com/user-attachments/assets/6b95b57a-3b01-49f0-ae43-c6a59a97851b" />

# Qdrant: 
Banco de dados vetorial para buscas semânticas em documentos de processos.

<img width="1867" height="932" alt="Captura de tela 2025-09-15 201437" src="https://github.com/user-attachments/assets/69d50061-66c1-4d88-a717-b97f45beab8e" />


Salesforce: Acessado em tempo real para buscar dados de clientes, oportunidades (OPs) e contatos.

# 🛠️ Tecnologias Utilizadas

FastAPI

LangChain

Pydantic

SQLAlchemy

Alembic

Front-end

Streamlit

Bancos de Dados

PostgreSQL

Qdrant (Banco Vetorial)

Autenticação

Keycloak (OIDC)

Linguagem

Python 3.10+




