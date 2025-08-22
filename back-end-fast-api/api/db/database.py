# api/db/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus  # 👈 1. IMPORTE A FUNÇÃO 'quote_plus'

# Importa as configurações (usuário, senha, host, etc.) do seu arquivo .env
from api.core.config import settings


# 👇 2. CODIFIQUE A SENHA ANTES DE USÁ-LA NA URL
password_encoded = quote_plus(settings.DB_PASSWORD)

# Monta a URL de conexão para o PostgreSQL usando as configurações
# O formato é: "postgresql://usuario:senha@host:porta/nomedobanco"
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.DB_USER}:{password_encoded}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"


# O 'engine' é o ponto de entrada principal do SQLAlchemy para o banco de dados.
# Ele gerencia as conexões.
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Cada instância de SessionLocal será uma sessão de banco de dados.
# Usaremos isso para interagir com o banco de dados em cada requisição.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Esta é a classe "mãe" que nossos modelos de tabela (em models.py) irão herdar.
# É a 'Base' que estava faltando e causando o erro de importação.
Base = declarative_base()