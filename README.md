Mbot - Assistente Corporativo com IA

Este repositório contém o código-fonte do Mbot, um assistente de IA conversacional projetado para otimizar o acesso a informações internas e acelerar processos de consulta para equipes de atendimento e suporte ao cliente.



🎯 Objetivo do Projeto

O objetivo principal do Mbot é servir como um ponto central de consulta para dúvidas sobre processos internos e dados de clientes. Ele capacita a equipe de atendimento a obter respostas rápidas e precisas, diretamente de fontes de dados oficiais como o Salesforce, sem a necessidade de navegar por múltiplas telas ou consultar diferentes departamentos.



Para a Equipe de Atendimento: Reduz o tempo de resposta ao cliente, aumenta a precisão das informações e padroniza o conhecimento sobre processos.



Para a Empresa: Centraliza o conhecimento, diminui a carga de trabalho em consultas repetitivas e cria uma base para futuras integrações, como a consulta de dados no SAP.



🏛️ Arquitetura do Sistema

O projeto é construído em uma arquitetura de microsserviços desacoplada, garantindo escalabilidade, segurança e manutenibilidade.



Front-end (front-end-stream-lit): Uma interface de usuário web interativa construída com Streamlit. É responsável por gerenciar a autenticação do usuário, exibir a conversa e se comunicar com o back-end via requisições HTTP.



Back-end (back-end-fast-api): O cérebro da aplicação. Uma API RESTful robusta e assíncrona construída com FastAPI. Suas responsabilidades incluem:



Validar a identidade do usuário a cada requisição.



Orquestrar a lógica de IA com LangChain.



Conectar-se às fontes de dados (PostgreSQL, Qdrant, Salesforce).



Persistir o histórico das conversas.



Fontes de Dados:



PostgreSQL: Armazena dados relacionais, como informações de usuários e o histórico das conversas.



Qdrant: Um banco de dados vetorial de alta performance que armazena o conhecimento sobre processos internos, permitindo buscas semânticas rápidas.



Salesforce: Acessado em tempo real para buscar dados de clientes, oportunidades (OPs) e contatos.



🛠️ Tecnologias Utilizadas

Este projeto utiliza um conjunto de tecnologias modernas para garantir performance e segurança:



Back-end:



FastAPI: Framework web de alta performance para construir APIs com Python, com suporte nativo a assincronismo.



LangChain: Framework para orquestrar a lógica da IA, gerenciando prompts, memória e a integração com modelos de linguagem.



Pydantic: Para validação de dados robusta e automática nos modelos da API.



PostgreSQL: Banco de dados relacional para persistência de dados.



SQLAlchemy: ORM para interagir com o PostgreSQL de forma segura e eficiente.



Alembic: Ferramenta para gerenciar migrações de schema do banco de dados.



Qdrant: Banco de dados vetorial para a busca de similaridade em documentos de processos.



Front-end:



Streamlit: Framework para criar interfaces de usuário web interativas para aplicações de dados e IA com Python puro.



Autenticação e Segurança:



Keycloak: Solução de gerenciamento de identidade e acesso (IAM) que lida com o login dos usuários de forma segura via padrão OIDC.



🚀 Como Executar o Projeto

Siga os passos abaixo para configurar e rodar o ambiente de desenvolvimento local.



Pré-requisitos

Python 3.10+



Docker (para rodar Keycloak, PostgreSQL e Qdrant, se desejar)



Conta na OpenAI para a chave de API



1\. Configuração do Back-end

Navegue até a pasta do back-end:



cd back-end-fast-api



Crie e ative um ambiente virtual:



python -m venv .venv

\# No Windows:

.\\.venv\\Scripts\\activate

\# No Linux/Mac:

source .venv/bin/activate



Instale as dependências:



pip install -r requirements.txt



Crie um arquivo .env a partir do .env.example e preencha com suas credenciais (Keycloak, Banco de Dados, OpenAI, Salesforce).



Execute o servidor da API:



uvicorn api.main:app --reload



O servidor estará rodando em http://localhost:8000.



2\. Configuração do Front-end

Abra um novo terminal.



Navegue até a pasta do front-end:



cd front-end-stream-lit



Crie e ative um ambiente virtual (siga os mesmos passos do back-end).



Instale as dependências:



pip install -r requirements.txt



Crie um arquivo .env e preencha com as configurações do Keycloak e da API.



Execute a aplicação Streamlit:



streamlit run main.py



A aplicação estará acessível em http://localhost:8501.

