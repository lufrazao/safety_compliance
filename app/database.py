"""
Database configuration and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
import os

# Database URL - SQLite localmente, PostgreSQL no Railway (obrigatório para persistir dados)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./compliance.db")

# Aviso: SQLite em produção (Railway) = dados perdidos a cada deploy
if "sqlite" in DATABASE_URL and (os.getenv("RAILWAY_ENVIRONMENT_NAME") or os.getenv("RAILWAY_PUBLIC_DOMAIN")):
    print("⚠️  AVISO: DATABASE_URL não definido. Usando SQLite - aeroportos e dados serão PERDIDOS a cada deploy!")
    print("   Solução: Railway → serviço app → Variables → Add Reference → PostgreSQL DATABASE_URL")

# Railway uses postgres:// but SQLAlchemy expects postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_pre_ping=True if "postgresql" in DATABASE_URL else False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
