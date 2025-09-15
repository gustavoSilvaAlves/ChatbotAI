from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus


from api.core.config import settings



password_encoded = quote_plus(settings.DB_PASSWORD)


SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.DB_USER}:{password_encoded}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"



engine = create_engine(SQLALCHEMY_DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()