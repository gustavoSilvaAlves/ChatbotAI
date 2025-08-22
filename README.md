# 🤖 Mbot - Assistente Corporativo com IA
O Mbot é um assistente de IA conversacional projetado para otimizar o acesso a informações internas e acelerar processos de consulta as nossas bases de dados(Salesforce, SAP e Conhecimentos internos) para as diversas equipes da empresa incluindo o atendimento e suporte ao cliente.

<img width="1896" height="945" alt="Captura de tela 2025-08-22 185903" src="https://github.com/user-attachments/assets/712da788-da07-4332-bfc9-1ef3aed85072" />


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

# Postgres

<img width="1669" height="881" alt="Captura de tela 2025-08-22 190141" src="https://github.com/user-attachments/assets/e3fb7242-cae4-44b2-9426-6fec32235787" />

# Qdrant

<img width="1913" height="942" alt="Captura de tela 2025-08-22 190612" src="https://github.com/user-attachments/assets/5ab59563-4e70-40a5-9b3a-ae2cc8e228b5" />

# FastAPI

<img width="1898" height="942" alt="Captura de tela 2025-08-22 190021" src="https://github.com/user-attachments/assets/729af254-dbcf-4e3f-868c-1a438906dfb2" />


# Autenticação & Infraestrutura

🔑 Keycloak: Solução de gerenciamento de identidade e acesso (IAM).

<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-original.svg" width="20" /> Docker: Recomendado para rodar os serviços em ambiente de produção.


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

