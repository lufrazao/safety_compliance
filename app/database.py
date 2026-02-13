"""
Database configuration and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
import os

# Database URL - SQLite localmente, PostgreSQL no Railway (obrigatório para persistir dados)
# Preferir DATABASE_PUBLIC_URL: postgres.railway.internal só resolve dentro da rede privada do Railway.
_raw_url = os.getenv("DATABASE_PUBLIC_URL") or os.getenv("DATABASE_URL") or "sqlite:///./compliance.db"
if "railway.internal" in _raw_url:
    public = os.getenv("DATABASE_PUBLIC_URL")
    if not public:
        raise RuntimeError(
            "DATABASE_URL usa postgres.railway.internal (host interno) que não resolve neste ambiente. "
            "Adicione a variável DATABASE_PUBLIC_URL: Railway → serviço app → Variables → "
            "Add Reference → PostgreSQL → DATABASE_PUBLIC_URL"
        )
    _raw_url = public
DATABASE_URL = _raw_url

# Aviso: SQLite em produção (Railway) = dados perdidos a cada deploy
if "sqlite" in DATABASE_URL and (os.getenv("RAILWAY_ENVIRONMENT_NAME") or os.getenv("RAILWAY_PUBLIC_DOMAIN")):
    print("⚠️  AVISO: DATABASE_URL não definido. Usando SQLite - aeroportos e dados serão PERDIDOS a cada deploy!")
    print("   Solução: Railway → serviço app → Variables → Add Reference → PostgreSQL DATABASE_PUBLIC_URL (ou DATABASE_URL)")

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
