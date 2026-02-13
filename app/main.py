"""
FastAPI application for airport compliance management.
"""
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response, JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uvicorn
import os
import json
import shutil
import base64
import hashlib
from pathlib import Path

from app.database import get_db, init_db
from app import schemas
from app.compliance_engine import ComplianceEngine
from app.models import Airport, ANACAirport, Regulation, ComplianceRecord, DocumentAttachment, AirportSize, AirportType
from app.services.anac_sync import ANACSyncService

app = FastAPI(
    title="ANAC Airport Compliance System",
    description="Compliance management system for Brazilian airports",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Autenticação por senha. Se APP_PASSWORD estiver definido, exige login (apenas senha).
APP_PASSWORD = os.getenv("APP_PASSWORD")
AUTH_COOKIE = "anac_auth"
AUTH_COOKIE_SALT = "anac_compliance_salt"


def _auth_token():
    """Token válido para cookie (derivado da senha)."""
    if not APP_PASSWORD:
        return None
    return hashlib.sha256((APP_PASSWORD + AUTH_COOKIE_SALT).encode()).hexdigest()


def _verify_auth(request: Request) -> bool:
    """Verifica cookie de autenticação ou Basic Auth (fallback)."""
    if not APP_PASSWORD:
        return True
    # Cookie (login com apenas senha)
    token = request.cookies.get(AUTH_COOKIE)
    if token == _auth_token():
        return True
    # Fallback: Basic Auth (username pode ser qualquer)
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Basic "):
        try:
            decoded = base64.b64decode(auth[6:]).decode("utf-8")
            _, password = decoded.split(":", 1)
            return password == APP_PASSWORD
        except Exception:
            pass
    return False


def _login_page_html() -> str:
    """Página de login com apenas campo de senha."""
    return """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Sistema de Conformidade ANAC</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #F8F9FA; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-box { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,51,102,0.1); border: 1px solid #E4E7EB; max-width: 360px; width: 100%; }
        .login-box h1 { color: #003366; font-size: 22px; margin-bottom: 8px; }
        .login-box p { color: #64748B; font-size: 14px; margin-bottom: 24px; }
        .login-box label { display: block; font-weight: 500; color: #475569; margin-bottom: 6px; font-size: 14px; }
        .login-box input { width: 100%; padding: 12px 14px; border: 2px solid #E4E7EB; border-radius: 8px; font-size: 16px; }
        .login-box input:focus { outline: none; border-color: #003366; }
        .login-box button { width: 100%; padding: 12px; background: #003366; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; margin-top: 16px; }
        .login-box button:hover { background: #002244; }
        .login-box .error { color: #DC2626; font-size: 13px; margin-top: 8px; display: none; }
    </style>
</head>
<body>
    <div class="login-box">
        <h1>Sistema de Conformidade ANAC</h1>
        <p>Entre com a senha de acesso</p>
        <form id="loginForm">
            <label for="password">Senha</label>
            <input type="password" id="password" name="password" placeholder="Digite a senha" required autofocus>
            <div class="error" id="error">Senha incorreta. Tente novamente.</div>
            <button type="submit">Entrar</button>
        </form>
    </div>
    <script>
        document.getElementById('loginForm').onsubmit = async (e) => {
            e.preventDefault();
            const password = document.getElementById('password').value;
            const errEl = document.getElementById('error');
            errEl.style.display = 'none';
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: password }),
                credentials: 'include'
            });
            if (res.ok) {
                window.location.href = '/';
            } else {
                errEl.style.display = 'block';
                document.getElementById('password').value = '';
                document.getElementById('password').focus();
            }
        };
    </script>
</body>
</html>"""


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """Exige senha quando APP_PASSWORD está definido. Login via cookie (apenas senha)."""
    if not APP_PASSWORD:
        return await call_next(request)
    if request.url.path == "/api/login":
        return await call_next(request)
    if _verify_auth(request):
        return await call_next(request)
    if request.url.path in ("/", "/index.html") or request.url.path.startswith("/static"):
        return Response(content=_login_page_html(), media_type="text/html")
    return JSONResponse(
        status_code=401,
        content={"detail": "Autenticação necessária. Acesse a página inicial e informe a senha."},
    )


# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


def _run_anac_enrichment_migration():
    """Adiciona colunas de enriquecimento em anac_airports se não existirem."""
    try:
        from sqlalchemy import text
        from app.database import engine
        cols = [("usage_class", "VARCHAR(20)"), ("avsec_classification", "VARCHAR(10)"),
                ("aircraft_size_category", "VARCHAR(5)"), ("number_of_runways", "INTEGER DEFAULT 1")]
        with engine.connect() as conn:
            for col_name, col_type in cols:
                try:
                    conn.execute(text(f"ALTER TABLE anac_airports ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
                except Exception as e:
                    if "duplicate" not in str(e).lower() and "already exists" not in str(e).lower():
                        raise
    except Exception:
        pass


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    _run_anac_enrichment_migration()


@app.post("/api/login")
async def login(request: Request):
    """Valida senha e define cookie de autenticação. Aceita {password} no body."""
    if not APP_PASSWORD:
        return {"ok": True}
    try:
        body = await request.json()
        password = body.get("password", "")
        if password != APP_PASSWORD:
            raise HTTPException(status_code=401, detail="Senha incorreta")
        response = JSONResponse(content={"ok": True})
        token = _auth_token()
        secure = request.url.scheme == "https"
        response.set_cookie(
            key=AUTH_COOKIE,
            value=token,
            httponly=True,
            samesite="lax",
            secure=secure,
            path="/",
            max_age=60 * 60 * 24 * 7,  # 7 dias
        )
        return response
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Requisição inválida")


@app.post("/api/seed")
async def run_seed():
    """
    Popula o banco com normas RBAC, dados de exemplo e bootstrap anac_airports.
    Útil para setup inicial no Railway.
    """
    try:
        from app.seed_data import seed_regulations, seed_sample_airports, seed_anac_airports_bootstrap
        seed_regulations()
        seed_sample_airports()
        seed_anac_airports_bootstrap()
        return {"message": "Seed concluído. Normas, aeroportos de exemplo e lista ANAC (15 principais) carregados."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/favicon.ico")
async def favicon():
    """Evita 404 no favicon - retorna 204 (sem conteúdo)."""
    return Response(status_code=204)

@app.get("/.well-known/appspecific/com.chrome.devtools.json")
async def chrome_devtools_config():
    """Chrome DevTools auto-requests this; return empty to avoid 404 logs."""
    return {}

@app.get("/")
async def root():
    """Serve the main web interface."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "message": "ANAC Airport Compliance System API",
        "version": "1.0.0",
        "endpoints": {
            "airports": "/api/airports",
            "regulations": "/api/regulations",
            "compliance": "/api/compliance"
        },
        "note": "Interface web disponível em /static/index.html ou abra http://localhost:8000 no navegador"
    }


# Airport endpoints
@app.post("/api/airports", response_model=schemas.AirportResponse, status_code=status.HTTP_201_CREATED)
async def create_airport(airport: schemas.AirportCreate, db: Session = Depends(get_db)):
    """Create a new airport profile."""
    # Check if code already exists
    existing = db.query(Airport).filter(Airport.code == airport.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Airport with code {airport.code} already exists"
        )
    
    airport_dict = airport.dict()
    
    # Calcular size e annual_passengers automaticamente a partir de usage_class
    if airport_dict.get('usage_class'):
        usage_class = airport_dict['usage_class']
        if usage_class == 'PRIVADO':
            airport_dict['size'] = AirportSize.SMALL
            airport_dict['annual_passengers'] = 0  # Privado não tem passageiros comerciais
        elif usage_class == 'I':
            airport_dict['size'] = AirportSize.SMALL
            airport_dict['annual_passengers'] = 100000  # Estimativa média para Classe I
        elif usage_class == 'II':
            airport_dict['size'] = AirportSize.MEDIUM
            airport_dict['annual_passengers'] = 600000  # Estimativa média para Classe II
        elif usage_class == 'III':
            airport_dict['size'] = AirportSize.LARGE
            airport_dict['annual_passengers'] = 3000000  # Estimativa média para Classe III
        elif usage_class == 'IV':
            airport_dict['size'] = AirportSize.INTERNATIONAL
            airport_dict['annual_passengers'] = 10000000  # Estimativa média para Classe IV
    elif not airport_dict.get('size'):
        # Fallback: se não houver usage_class, usar size se fornecido
        if not airport_dict.get('size'):
            airport_dict['size'] = AirportSize.SMALL  # Default
    
    db_airport = Airport(**airport_dict)
    db.add(db_airport)
    db.commit()
    db.refresh(db_airport)
    return db_airport


@app.get("/api/airports", response_model=List[schemas.AirportResponse])
async def list_airports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all airports."""
    airports = db.query(Airport).offset(skip).limit(limit).all()
    return airports


@app.get("/api/airports/{airport_id}", response_model=schemas.AirportResponse)
async def get_airport(airport_id: int, db: Session = Depends(get_db)):
    """Get a specific airport by ID."""
    airport = db.query(Airport).filter(Airport.id == airport_id).first()
    if not airport:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Airport with id {airport_id} not found"
        )
    return airport


@app.put("/api/airports/{airport_id}", response_model=schemas.AirportResponse)
async def update_airport(
    airport_id: int,
    airport_update: schemas.AirportCreate,
    db: Session = Depends(get_db)
):
    """Update an existing airport profile."""
    airport = db.query(Airport).filter(Airport.id == airport_id).first()
    if not airport:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Airport with id {airport_id} not found"
        )
    
    # Check if code is being changed and if new code already exists
    if airport_update.code != airport.code:
        existing = db.query(Airport).filter(Airport.code == airport_update.code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Airport with code {airport_update.code} already exists"
            )
    
    try:
        airport_dict = airport_update.model_dump() if hasattr(airport_update, 'model_dump') else airport_update.dict()
    except Exception:
        airport_dict = airport_update.dict()
    
    # Calcular size e annual_passengers automaticamente a partir de usage_class
    if airport_dict.get('usage_class'):
        usage_class = airport_dict['usage_class']
        if usage_class == 'PRIVADO':
            airport_dict['size'] = AirportSize.SMALL
            airport_dict['annual_passengers'] = 0  # Privado não tem passageiros comerciais
        elif usage_class == 'I':
            airport_dict['size'] = AirportSize.SMALL
            airport_dict['annual_passengers'] = 100000  # Estimativa média para Classe I
        elif usage_class == 'II':
            airport_dict['size'] = AirportSize.MEDIUM
            airport_dict['annual_passengers'] = 600000  # Estimativa média para Classe II
        elif usage_class == 'III':
            airport_dict['size'] = AirportSize.LARGE
            airport_dict['annual_passengers'] = 3000000  # Estimativa média para Classe III
        elif usage_class == 'IV':
            airport_dict['size'] = AirportSize.INTERNATIONAL
            airport_dict['annual_passengers'] = 10000000  # Estimativa média para Classe IV
    
    # Converter enums se vierem como string (compatibilidade)
    if isinstance(airport_dict.get('size'), str):
        airport_dict['size'] = AirportSize(airport_dict['size'])
    if isinstance(airport_dict.get('airport_type'), str):
        airport_dict['airport_type'] = AirportType(airport_dict['airport_type'])
    
    # Update all fields (apenas colunas que existem no modelo)
    model_keys = {c.key for c in Airport.__table__.columns}
    for key, value in airport_dict.items():
        if key in model_keys:
            setattr(airport, key, value)
    
    try:
        db.commit()
        db.refresh(airport)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return airport


@app.delete("/api/airports/{airport_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_airport(airport_id: int, db: Session = Depends(get_db)):
    """Delete an airport profile."""
    airport = db.query(Airport).filter(Airport.id == airport_id).first()
    if not airport:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Airport with id {airport_id} not found"
        )
    
    db.delete(airport)
    db.commit()
    return None


# ANAC Synchronization endpoints
def _infer_missing_lookup_fields(result: dict, airport: Airport) -> None:
    """Infere usage_class, avsec, aircraft_size quando ausentes no lookup."""
    ref = (result.get('reference_code') or getattr(airport, 'reference_code', None) or '').upper()
    usage = result.get('usage_class') or getattr(airport, 'usage_class', None)
    avsec = result.get('avsec_classification') or getattr(airport, 'avsec_classification', None)
    aircraft = result.get('aircraft_size_category') or getattr(airport, 'aircraft_size_category', None)
    passengers = getattr(airport, 'annual_passengers', None) or 0
    # Inferir aircraft_size_category a partir de reference_code (ex: 4C -> C)
    if not aircraft and len(ref) >= 2:
        letter = ref[-1]
        if letter in ('A', 'B'):
            result['aircraft_size_category'] = 'A/B'
        elif letter == 'C':
            result['aircraft_size_category'] = 'C'
        elif letter in ('D', 'E'):
            result['aircraft_size_category'] = 'D'
    # Inferir usage_class e avsec a partir de passageiros
    if not usage or not avsec:
        if passengers < 200000:
            result.setdefault('usage_class', 'I')
            result.setdefault('avsec_classification', 'AP-1')
        elif passengers < 1000000:
            result.setdefault('usage_class', 'II')
            result.setdefault('avsec_classification', 'AP-1')
        elif passengers < 5000000:
            result.setdefault('usage_class', 'III')
            result.setdefault('avsec_classification', 'AP-2')
        else:
            result.setdefault('usage_class', 'IV')
            result.setdefault('avsec_classification', 'AP-3')
    if not usage and airport.size:
        size_val = str(airport.size.value) if hasattr(airport.size, 'value') else str(airport.size)
        if size_val == 'small':
            result.setdefault('usage_class', 'I')
        elif size_val == 'medium':
            result.setdefault('usage_class', 'II')
        elif size_val == 'large':
            result.setdefault('usage_class', 'III')
        elif size_val == 'international':
            result.setdefault('usage_class', 'IV')


@app.get("/api/airports/lookup/{icao_code}")
async def lookup_airport_from_anac(
    icao_code: str,
    db: Session = Depends(get_db)
):
    """
    Busca dados de um aeroporto específico na lista oficial da ANAC.
    
    Retorna dados que podem ser usados para preencher o formulário automaticamente.
    Se a ANAC estiver indisponível, usa dados do banco local (se o aeroporto existir).
    """
    try:
        # Validar formato do código ICAO
        icao_code = icao_code.upper().strip()
        if len(icao_code) != 4 or not icao_code.isalpha():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Código ICAO deve ter exatamente 4 letras"
            )
        
        sync_service = ANACSyncService(db=db)
        
        # 1. Base interna primeiro (não chama ANAC externa)
        airport_data = sync_service.get_from_anac_airports_table(icao_code)
        if airport_data:
            anac_source = "anac_db"
        else:
            local_airport = db.query(Airport).filter(Airport.code == icao_code).first()
            if local_airport:
                at = local_airport.airport_type
                at_val = at.value if hasattr(at, 'value') else str(at) if at else ''
                result = {
                    "name": local_airport.name,
                    "code": local_airport.code,
                    "reference_code": local_airport.reference_code,
                    "usage_class": local_airport.usage_class,
                    "avsec_classification": local_airport.avsec_classification,
                    "aircraft_size_category": local_airport.aircraft_size_category,
                    "airport_type": at_val,
                    "source": "local",
                    "lookup_timestamp": datetime.utcnow().isoformat(),
                }
                _infer_missing_lookup_fields(result, local_airport)
                return result
            # 2. Só então tentar ANAC (ao vivo ou cache)
            anac_data, anac_source = sync_service.get_anac_data(use_cache_if_live_fails=True)
            if anac_data:
                airport_data = next((d for d in anac_data if d.get('code', '').upper() == icao_code), None)
                if airport_data:
                    anac_source = anac_source or "anac"
                else:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Aeroporto {icao_code} não encontrado na lista oficial da ANAC"
                    )
        
        if not airport_data:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Aeroporto não encontrado na base interna. Execute POST /api/seed para popular os dados iniciais ou preencha manualmente."
            )
        
        # Aeroporto encontrado - priorizar dados da ANAC; inferir só o que faltar
        calculated = {}
        if airport_data.get('category'):
            category_num = airport_data['category'].replace('C', '')
            if category_num.isdigit():
                cat_num = int(category_num)
                if cat_num <= 2:
                    calculated['estimated_annual_passengers'] = 100000
                elif cat_num <= 4:
                    calculated['estimated_annual_passengers'] = 600000
                elif cat_num <= 6:
                    calculated['estimated_annual_passengers'] = 3000000
                else:
                    calculated['estimated_annual_passengers'] = 10000000
        # Só inferir usage_class e avsec quando ausentes (dados Características Gerais têm prioridade)
        if not airport_data.get('usage_class') and calculated.get('estimated_annual_passengers'):
            p = calculated['estimated_annual_passengers']
            calculated['usage_class'] = 'I' if p <= 200000 else 'II' if p <= 1000000 else 'III' if p <= 5000000 else 'IV'
        if not airport_data.get('avsec_classification') and calculated.get('estimated_annual_passengers'):
            p = calculated['estimated_annual_passengers']
            calculated['avsec_classification'] = 'AP-1' if p < 600000 else 'AP-2' if p < 5000000 else 'AP-3'
        if not airport_data.get('aircraft_size_category') and airport_data.get('reference_code'):
            ref = airport_data['reference_code'].upper()
            if len(ref) >= 2:
                lt = ref[-1]
                calculated['aircraft_size_category'] = 'A/B' if lt in ('A','B') else 'C' if lt == 'C' else 'D'
        
        resp = {
            **airport_data,
            **calculated,
            "source": anac_source or "anac",
            "lookup_timestamp": datetime.utcnow().isoformat()
        }
        # ANAC lista aeródromos públicos: default commercial
        resp.setdefault("airport_type", "commercial")
        return resp
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar aeroporto: {str(e)}"
        )


@app.post("/api/airports/sync/anac/refresh-cache")
async def refresh_anac_cache(db: Session = Depends(get_db)):
    """
    Atualiza o cache de dados ANAC. Use quando o site da ANAC estiver acessível
    para que buscas futuras funcionem offline.
    """
    sync_service = ANACSyncService(db=db)
    data = sync_service.download_anac_data()
    if data:
        return {
            "success": True,
            "airports_count": len(data),
            "message": "Cache ANAC atualizado com sucesso."
        }
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Não foi possível baixar dados da ANAC. Tente novamente mais tarde."
    )


@app.post("/api/airports/sync/anac")
async def sync_airports_with_anac(
    dry_run: bool = False,
    db: Session = Depends(get_db)
):
    """
    Synchronize airports with ANAC's official list.
    
    Args:
        dry_run: If True, only show what would be changed without actually updating
        
    Returns:
        Sync results with statistics and changes
    """
    try:
        sync_service = ANACSyncService(db=db)
        
        # ANAC ao vivo ou cache
        anac_data, _ = sync_service.get_anac_data(use_cache_if_live_fails=True)
        
        if not anac_data:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Não foi possível obter dados da ANAC. Tente novamente ou use o endpoint /api/airports/sync/anac/refresh-cache para atualizar o cache."
            )
        
        # Perform synchronization
        results = sync_service.sync_airports(anac_data, dry_run=dry_run)
        
        return {
            "success": True,
            "dry_run": dry_run,
            "total_anac_airports": len(anac_data),
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro durante sincronização: {str(e)}"
        )


# Regulation endpoints
@app.post("/api/regulations", response_model=schemas.RegulationResponse, status_code=status.HTTP_201_CREATED)
async def create_regulation(regulation: schemas.RegulationCreate, db: Session = Depends(get_db)):
    """Create a new regulation."""
    existing = db.query(Regulation).filter(Regulation.code == regulation.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Regulation with code {regulation.code} already exists"
        )
    
    db_regulation = Regulation(**regulation.dict())
    db.add(db_regulation)
    db.commit()
    db.refresh(db_regulation)
    return db_regulation


@app.get("/api/regulations", response_model=List[schemas.RegulationResponse])
async def list_regulations(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    db: Session = Depends(get_db)
):
    """List all regulations, optionally filtered by safety category."""
    query = db.query(Regulation)
    if category:
        query = query.filter(Regulation.safety_category == category)
    regulations = query.offset(skip).limit(limit).all()
    return regulations


@app.get("/api/regulations/{regulation_id}", response_model=schemas.RegulationResponse)
async def get_regulation(regulation_id: int, db: Session = Depends(get_db)):
    """Get a specific regulation by ID."""
    regulation = db.query(Regulation).filter(Regulation.id == regulation_id).first()
    if not regulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Regulation with id {regulation_id} not found"
        )
    return regulation


# Compliance endpoints
@app.post("/api/compliance/check", response_model=schemas.ComplianceCheckResponse)
async def check_compliance(
    request: schemas.ComplianceCheckRequest,
    db: Session = Depends(get_db)
):
    """Perform a compliance check for an airport."""
    try:
        engine = ComplianceEngine(db)
        result = engine.check_compliance(request.airport_id)
    except Exception as e:
        import traceback
        error_detail = f"Erro ao verificar conformidade: {str(e)}\n{traceback.format_exc()}"
        print(f"ERROR in check_compliance: {error_detail}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )
    
    # Convert compliance records to response format
    records_response = []
    for record in result["compliance_records"]:
        # Get regulation - try multiple approaches to ensure we get it
        regulation = None
        
        # Approach 1: Try to access via relationship (if loaded)
        try:
            if hasattr(record, 'regulation') and record.regulation:
                regulation = record.regulation
        except Exception:
            pass
        
        # Approach 2: Query directly (most reliable)
        if not regulation:
            regulation = db.query(Regulation).filter(Regulation.id == record.regulation_id).first()
        
        # Approach 3: If still not found, try to merge the record into this session
        if not regulation and record.regulation_id:
            try:
                # Merge the record into this session to ensure we can access relationships
                record = db.merge(record)
                db.flush()
                if hasattr(record, 'regulation') and record.regulation:
                    regulation = record.regulation
                else:
                    regulation = db.query(Regulation).filter(Regulation.id == record.regulation_id).first()
            except Exception as e:
                import logging
                logging.warning(f"Error merging record {record.id}: {e}")
                # Final fallback: direct query
                regulation = db.query(Regulation).filter(Regulation.id == record.regulation_id).first()
        
        # Debug: Log if regulation is still not found
        if not regulation and record.regulation_id:
            import logging
            logging.error(f"CRITICAL: Regulation not found for record {record.id} with regulation_id {record.regulation_id} after all attempts")
        
        # Parse action_items if it's a JSON string
        action_items = None
        if record.action_items:
            try:
                if isinstance(record.action_items, str):
                    action_items = json.loads(record.action_items)
                else:
                    action_items = record.action_items
            except (json.JSONDecodeError, TypeError):
                action_items = None
        
        # Parse completed_action_items if it's a JSON string
        completed_action_items = None
        if record.completed_action_items:
            try:
                if isinstance(record.completed_action_items, str):
                    completed_action_items = json.loads(record.completed_action_items)
                else:
                    completed_action_items = record.completed_action_items
            except (json.JSONDecodeError, TypeError):
                completed_action_items = None
        
        # Parse action_item_due_dates if it's a JSON string
        action_item_due_dates = None
        if record.action_item_due_dates:
            try:
                if isinstance(record.action_item_due_dates, str):
                    action_item_due_dates = json.loads(record.action_item_due_dates)
                else:
                    action_item_due_dates = record.action_item_due_dates
            except (json.JSONDecodeError, TypeError):
                action_item_due_dates = None
        
        # Parse regulation JSON fields before validation
        regulation_dict = None
        if regulation:
            # Parse JSON strings for applies_to_sizes and applies_to_types
            applies_to_sizes = None
            if regulation.applies_to_sizes:
                try:
                    applies_to_sizes = json.loads(regulation.applies_to_sizes)
                except (json.JSONDecodeError, TypeError):
                    applies_to_sizes = None
            
            applies_to_types = None
            if regulation.applies_to_types:
                try:
                    applies_to_types = json.loads(regulation.applies_to_types)
                except (json.JSONDecodeError, TypeError):
                    applies_to_types = None
            
            # Convert enums to strings for JSON serialization (with error handling)
            try:
                safety_category_value = regulation.safety_category.value if hasattr(regulation.safety_category, 'value') else str(regulation.safety_category)
            except Exception as e:
                import logging
                logging.warning(f"Error getting safety_category for regulation {regulation.id}: {e}")
                safety_category_value = str(regulation.safety_category) if regulation.safety_category else None
                
            try:
                requirement_classification_value = regulation.requirement_classification.value if regulation.requirement_classification and hasattr(regulation.requirement_classification, 'value') else (str(regulation.requirement_classification) if regulation.requirement_classification else None)
            except Exception as e:
                import logging
                logging.warning(f"Error getting requirement_classification for regulation {regulation.id}: {e}")
                requirement_classification_value = str(regulation.requirement_classification) if regulation.requirement_classification else None
                
            try:
                evaluation_type_value = regulation.evaluation_type.value if regulation.evaluation_type and hasattr(regulation.evaluation_type, 'value') else (str(regulation.evaluation_type) if regulation.evaluation_type else None)
            except Exception as e:
                import logging
                logging.warning(f"Error getting evaluation_type for regulation {regulation.id}: {e}")
                evaluation_type_value = str(regulation.evaluation_type) if regulation.evaluation_type else None
            
            try:
                regulation_dict = {
                    "id": regulation.id,
                    "code": regulation.code,
                    "title": regulation.title,
                    "description": regulation.description,
                    "safety_category": safety_category_value,
                    "requirement_classification": requirement_classification_value,
                    "evaluation_type": evaluation_type_value,
                    "weight": regulation.weight,
                    "anac_reference": regulation.anac_reference,
                    "applies_to_sizes": applies_to_sizes,
                    "applies_to_types": applies_to_types,
                    "min_passengers": regulation.min_passengers,
                    "requires_international": regulation.requires_international,
                    "requires_cargo": regulation.requires_cargo,
                    "requires_maintenance": regulation.requires_maintenance,
                    "min_runways": regulation.min_runways,
                    "min_aircraft_weight": regulation.min_aircraft_weight,
                    "requirements": regulation.requirements,
                    "expected_performance": regulation.expected_performance
                }
            except Exception as e:
                import logging
                import traceback
                logging.error(f"Error creating regulation_dict for regulation {regulation.id}: {e}")
                logging.error(traceback.format_exc())
                regulation_dict = None
        
        # Parse custom_fields if it's a JSON string
        custom_fields = None
        if record.custom_fields:
            try:
                if isinstance(record.custom_fields, str):
                    custom_fields = record.custom_fields  # Keep as string for API response
                else:
                    custom_fields = json.dumps(record.custom_fields) if record.custom_fields else None
            except (json.JSONDecodeError, TypeError):
                custom_fields = None
        
        # Create regulation response, handling errors gracefully
        regulation_response = None
        if regulation_dict:
            try:
                regulation_response = schemas.RegulationResponse(**regulation_dict)
            except Exception as e:
                import logging
                import traceback
                logging.error(f"Error creating RegulationResponse for record {record.id}, regulation {record.regulation_id}: {e}")
                logging.error(traceback.format_exc())
                # Create a minimal regulation response as fallback
                try:
                    regulation_response = schemas.RegulationResponse(
                        id=regulation_dict.get("id"),
                        code=regulation_dict.get("code", "N/A"),
                        title=regulation_dict.get("title", "Norma não encontrada"),
                        description=regulation_dict.get("description", ""),
                        safety_category=regulation_dict.get("safety_category", "unknown"),
                        requirement_classification=regulation_dict.get("requirement_classification"),
                        evaluation_type=regulation_dict.get("evaluation_type"),
                        weight=regulation_dict.get("weight"),
                        anac_reference=regulation_dict.get("anac_reference"),
                        applies_to_sizes=regulation_dict.get("applies_to_sizes"),
                        applies_to_types=regulation_dict.get("applies_to_types"),
                        min_passengers=regulation_dict.get("min_passengers"),
                        requires_international=regulation_dict.get("requires_international"),
                        requires_cargo=regulation_dict.get("requires_cargo"),
                        requires_maintenance=regulation_dict.get("requires_maintenance"),
                        min_runways=regulation_dict.get("min_runways"),
                        min_aircraft_weight=regulation_dict.get("min_aircraft_weight"),
                        requirements=regulation_dict.get("requirements", ""),
                        expected_performance=regulation_dict.get("expected_performance")
                    )
                except Exception as e2:
                    import logging
                    logging.error(f"Failed to create minimal RegulationResponse: {e2}")
        
        record_dict = {
            "id": record.id,
            "airport_id": record.airport_id,
            "regulation_id": record.regulation_id,
            "status": record.status,
            "notes": record.notes,
            "docs_score": record.docs_score,
            "tops_score": record.tops_score,
            "weighted_score": record.weighted_score,
            "is_essential_compliant": record.is_essential_compliant,
            "action_items": action_items,
            "completed_action_items": completed_action_items,
            "action_item_due_dates": action_item_due_dates,
            "custom_fields": custom_fields,
            "last_verified": record.last_verified,
            "verified_by": record.verified_by,
            "regulation": regulation_response
        }
        records_response.append(schemas.ComplianceRecordResponse(**record_dict))
    
    return schemas.ComplianceCheckResponse(
        airport_id=result["airport_id"],
        total_regulations=result["total_regulations"],
        applicable_regulations=result["applicable_regulations"],
        compliant_count=result["compliant_count"],
        non_compliant_count=result["non_compliant_count"],
        partial_count=result["partial_count"],
        pending_count=result["pending_count"],
        compliance_records=records_response,
        recommendations=result["recommendations"],
        anac_scores=result.get("anac_scores")
    )


@app.get("/api/compliance/airport/{airport_id}", response_model=List[schemas.ComplianceRecordResponse])
async def get_airport_compliance(airport_id: int, db: Session = Depends(get_db)):
    """Get all compliance records for an airport."""
    records = db.query(ComplianceRecord).filter(
        ComplianceRecord.airport_id == airport_id
    ).all()
    
    records_response = []
    for record in records:
        regulation = db.query(Regulation).filter(Regulation.id == record.regulation_id).first()
        
        # Parse action_items if it's a JSON string
        action_items = None
        if record.action_items:
            try:
                if isinstance(record.action_items, str):
                    action_items = json.loads(record.action_items)
                else:
                    action_items = record.action_items
            except (json.JSONDecodeError, TypeError):
                action_items = None
        
        # Parse completed_action_items if it's a JSON string
        completed_action_items = None
        if record.completed_action_items:
            try:
                if isinstance(record.completed_action_items, str):
                    completed_action_items = json.loads(record.completed_action_items)
                else:
                    completed_action_items = record.completed_action_items
            except (json.JSONDecodeError, TypeError):
                completed_action_items = None
        
        # Parse action_item_due_dates if it's a JSON string
        action_item_due_dates = None
        if record.action_item_due_dates:
            try:
                if isinstance(record.action_item_due_dates, str):
                    action_item_due_dates = json.loads(record.action_item_due_dates)
                else:
                    action_item_due_dates = record.action_item_due_dates
            except (json.JSONDecodeError, TypeError):
                action_item_due_dates = None
        
        # Parse regulation JSON fields before validation
        regulation_dict = None
        if regulation:
            # Parse JSON strings for applies_to_sizes and applies_to_types
            applies_to_sizes = None
            if regulation.applies_to_sizes:
                try:
                    applies_to_sizes = json.loads(regulation.applies_to_sizes)
                except (json.JSONDecodeError, TypeError):
                    applies_to_sizes = None
            
            applies_to_types = None
            if regulation.applies_to_types:
                try:
                    applies_to_types = json.loads(regulation.applies_to_types)
                except (json.JSONDecodeError, TypeError):
                    applies_to_types = None
            
            # Convert enums to strings for JSON serialization
            safety_category_value = regulation.safety_category.value if hasattr(regulation.safety_category, 'value') else str(regulation.safety_category)
            requirement_classification_value = regulation.requirement_classification.value if regulation.requirement_classification and hasattr(regulation.requirement_classification, 'value') else (str(regulation.requirement_classification) if regulation.requirement_classification else None)
            evaluation_type_value = regulation.evaluation_type.value if regulation.evaluation_type and hasattr(regulation.evaluation_type, 'value') else (str(regulation.evaluation_type) if regulation.evaluation_type else None)
            
            regulation_dict = {
                "id": regulation.id,
                "code": regulation.code,
                "title": regulation.title,
                "description": regulation.description,
                "safety_category": safety_category_value,
                "requirement_classification": requirement_classification_value,
                "evaluation_type": evaluation_type_value,
                "weight": regulation.weight,
                "anac_reference": regulation.anac_reference,
                "applies_to_sizes": applies_to_sizes,
                "applies_to_types": applies_to_types,
                "min_passengers": regulation.min_passengers,
                "requires_international": regulation.requires_international,
                "requires_cargo": regulation.requires_cargo,
                "requires_maintenance": regulation.requires_maintenance,
                "min_runways": regulation.min_runways,
                "min_aircraft_weight": regulation.min_aircraft_weight,
                "requirements": regulation.requirements,
                "expected_performance": regulation.expected_performance
            }
        
        # Parse custom_fields if it's a JSON string
        custom_fields = None
        if record.custom_fields:
            try:
                if isinstance(record.custom_fields, str):
                    custom_fields = record.custom_fields  # Keep as string for API response
                else:
                    custom_fields = json.dumps(record.custom_fields) if record.custom_fields else None
            except (json.JSONDecodeError, TypeError):
                custom_fields = None
        
        record_dict = {
            "id": record.id,
            "airport_id": record.airport_id,
            "regulation_id": record.regulation_id,
            "status": record.status,
            "notes": record.notes,
            "docs_score": record.docs_score,
            "tops_score": record.tops_score,
            "weighted_score": record.weighted_score,
            "is_essential_compliant": record.is_essential_compliant,
            "action_items": action_items,
            "completed_action_items": completed_action_items,
            "action_item_due_dates": action_item_due_dates,
            "custom_fields": custom_fields,
            "last_verified": record.last_verified,
            "verified_by": record.verified_by,
            "regulation": schemas.RegulationResponse(**regulation_dict) if regulation_dict else None
        }
        records_response.append(schemas.ComplianceRecordResponse(**record_dict))
    
    return records_response


@app.get("/api/compliance/records/{record_id}", response_model=schemas.ComplianceRecordResponse)
async def get_compliance_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific compliance record by ID."""
    record = db.query(ComplianceRecord).filter(ComplianceRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compliance record with id {record_id} not found"
        )
    
    regulation = db.query(Regulation).filter(Regulation.id == record.regulation_id).first()
    
    # Parse regulation JSON fields before validation
    regulation_dict = None
    if regulation:
        # Parse JSON strings for applies_to_sizes and applies_to_types
        applies_to_sizes = None
        if regulation.applies_to_sizes:
            try:
                applies_to_sizes = json.loads(regulation.applies_to_sizes)
            except (json.JSONDecodeError, TypeError):
                applies_to_sizes = None
        
        applies_to_types = None
        if regulation.applies_to_types:
            try:
                applies_to_types = json.loads(regulation.applies_to_types)
            except (json.JSONDecodeError, TypeError):
                applies_to_types = None
        
        # Convert enums to strings for JSON serialization
        safety_category_value = regulation.safety_category.value if hasattr(regulation.safety_category, 'value') else str(regulation.safety_category)
        requirement_classification_value = regulation.requirement_classification.value if regulation.requirement_classification and hasattr(regulation.requirement_classification, 'value') else (str(regulation.requirement_classification) if regulation.requirement_classification else None)
        evaluation_type_value = regulation.evaluation_type.value if regulation.evaluation_type and hasattr(regulation.evaluation_type, 'value') else (str(regulation.evaluation_type) if regulation.evaluation_type else None)
        
        regulation_dict = {
            "id": regulation.id,
            "code": regulation.code,
            "title": regulation.title,
            "description": regulation.description,
            "safety_category": safety_category_value,
            "requirement_classification": requirement_classification_value,
            "evaluation_type": evaluation_type_value,
            "weight": regulation.weight,
            "anac_reference": regulation.anac_reference,
            "applies_to_sizes": applies_to_sizes,
            "applies_to_types": applies_to_types,
            "min_passengers": regulation.min_passengers,
            "requires_international": regulation.requires_international,
            "requires_cargo": regulation.requires_cargo,
            "requires_maintenance": regulation.requires_maintenance,
            "min_runways": regulation.min_runways,
            "min_aircraft_weight": regulation.min_aircraft_weight,
            "requirements": regulation.requirements,
            "expected_performance": regulation.expected_performance
        }
    
    # Parse action_items if it's a JSON string
    action_items = None
    if record.action_items:
        try:
            if isinstance(record.action_items, str):
                action_items = json.loads(record.action_items)
            else:
                action_items = record.action_items
        except (json.JSONDecodeError, TypeError):
            action_items = None
    
    # Parse completed_action_items if it's a JSON string
    completed_action_items = None
    if record.completed_action_items:
        try:
            if isinstance(record.completed_action_items, str):
                completed_action_items = json.loads(record.completed_action_items)
            else:
                completed_action_items = record.completed_action_items
        except (json.JSONDecodeError, TypeError):
            completed_action_items = None
    
    # Parse action_item_due_dates if it's a JSON string
    action_item_due_dates = None
    if record.action_item_due_dates:
        try:
            if isinstance(record.action_item_due_dates, str):
                action_item_due_dates = json.loads(record.action_item_due_dates)
            else:
                action_item_due_dates = record.action_item_due_dates
        except (json.JSONDecodeError, TypeError):
            action_item_due_dates = None
    
    # Parse custom_fields if it's a JSON string
    custom_fields = None
    if record.custom_fields:
        try:
            if isinstance(record.custom_fields, str):
                # Try to parse as JSON, but keep as string if it fails (for backward compatibility)
                try:
                    custom_fields = json.loads(record.custom_fields)
                except json.JSONDecodeError:
                    custom_fields = record.custom_fields  # Keep as string if not valid JSON
            else:
                custom_fields = record.custom_fields
        except (json.JSONDecodeError, TypeError):
            custom_fields = None
    
    # Build regulation response safely
    regulation_response = None
    if regulation_dict:
        try:
            # Ensure all enum values are properly converted
            if regulation_dict.get("safety_category"):
                if isinstance(regulation_dict["safety_category"], str):
                    from app.models import SafetyCategory
                    regulation_dict["safety_category"] = SafetyCategory(regulation_dict["safety_category"])
            if regulation_dict.get("requirement_classification"):
                if isinstance(regulation_dict["requirement_classification"], str):
                    from app.models import RequirementClassification
                    regulation_dict["requirement_classification"] = RequirementClassification(regulation_dict["requirement_classification"])
            if regulation_dict.get("evaluation_type"):
                if isinstance(regulation_dict["evaluation_type"], str):
                    from app.models import EvaluationType
                    regulation_dict["evaluation_type"] = EvaluationType(regulation_dict["evaluation_type"])
            
            regulation_response = schemas.RegulationResponse(**regulation_dict)
        except Exception as e:
            # Log error but don't fail the request
            import traceback
            print(f"⚠️  Erro ao criar RegulationResponse: {e}")
            print(f"   regulation_dict: {regulation_dict}")
            traceback.print_exc()
            regulation_response = None
    
    # Ensure status is properly serialized
    status_value = record.status
    if hasattr(status_value, 'value'):
        status_value = status_value.value
    elif not isinstance(status_value, str):
        status_value = str(status_value)
    
    record_dict = {
        "id": record.id,
        "airport_id": record.airport_id,
        "regulation_id": record.regulation_id,
        "status": status_value,
        "notes": record.notes,
        "docs_score": record.docs_score,
        "tops_score": record.tops_score,
        "weighted_score": record.weighted_score,
        "is_essential_compliant": record.is_essential_compliant,
        "action_items": action_items,
        "completed_action_items": completed_action_items,
        "action_item_due_dates": action_item_due_dates,
        "custom_fields": custom_fields,
        "last_verified": record.last_verified,
        "verified_by": record.verified_by,
        "regulation": regulation_response
    }
    
    try:
        return schemas.ComplianceRecordResponse(**record_dict)
    except Exception as e:
        # Log the full error for debugging
        import traceback
        print(f"❌ Erro ao criar ComplianceRecordResponse: {e}")
        print(f"   record_dict keys: {list(record_dict.keys())}")
        print(f"   record.status type: {type(record.status)}")
        print(f"   record.status value: {record.status}")
        print(f"   status_value: {status_value}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar resposta: {str(e)}"
        )


@app.put("/api/compliance/records/{record_id}", response_model=schemas.ComplianceRecordResponse)
async def update_compliance_record(
    record_id: int,
    update: schemas.ComplianceRecordUpdate,
    db: Session = Depends(get_db)
):
    """Update a compliance record."""
    from app.models import ComplianceStatus
    
    # Validate and convert status if provided
    status_value = update.status
    if status_value is not None:
        # Pydantic should handle the conversion, but we'll validate it
        if isinstance(status_value, str):
            try:
                status_value = ComplianceStatus(status_value)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status value: {status_value}. Must be one of: {[e.value for e in ComplianceStatus]}"
                )
        elif not isinstance(status_value, ComplianceStatus):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Status must be a ComplianceStatus enum or valid string value"
            )
    
    engine = ComplianceEngine(db)
    try:
        record = engine.update_compliance_status(
            record_id=record_id,
            status=status_value,
            notes=update.notes,
            action_items=update.action_items,
            completed_action_items=update.completed_action_items,
            action_item_due_dates=update.action_item_due_dates,
            verified_by=update.verified_by,
            custom_fields=update.custom_fields
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    regulation = db.query(Regulation).filter(Regulation.id == record.regulation_id).first()
    
    # Parse regulation JSON fields before validation
    regulation_dict = None
    if regulation:
        # Parse JSON strings for applies_to_sizes and applies_to_types
        applies_to_sizes = None
        if regulation.applies_to_sizes:
            try:
                applies_to_sizes = json.loads(regulation.applies_to_sizes)
            except (json.JSONDecodeError, TypeError):
                applies_to_sizes = None
        
        applies_to_types = None
        if regulation.applies_to_types:
            try:
                applies_to_types = json.loads(regulation.applies_to_types)
            except (json.JSONDecodeError, TypeError):
                applies_to_types = None
        
        regulation_dict = {
            "id": regulation.id,
            "code": regulation.code,
            "title": regulation.title,
            "description": regulation.description,
            "safety_category": regulation.safety_category,
            "requirement_classification": regulation.requirement_classification,
            "evaluation_type": regulation.evaluation_type,
            "weight": regulation.weight,
            "anac_reference": regulation.anac_reference,
            "applies_to_sizes": applies_to_sizes,
            "applies_to_types": applies_to_types,
            "min_passengers": regulation.min_passengers,
            "requires_international": regulation.requires_international,
            "requires_cargo": regulation.requires_cargo,
            "requires_maintenance": regulation.requires_maintenance,
            "min_runways": regulation.min_runways,
            "min_aircraft_weight": regulation.min_aircraft_weight,
            "requirements": regulation.requirements,
            "expected_performance": regulation.expected_performance
        }
    
    # Parse action_items if it's a JSON string
    action_items = None
    if record.action_items:
        try:
            if isinstance(record.action_items, str):
                action_items = json.loads(record.action_items)
            else:
                action_items = record.action_items
        except (json.JSONDecodeError, TypeError):
            action_items = None
    
    # Parse completed_action_items if it's a JSON string
    completed_action_items = None
    if record.completed_action_items:
        try:
            if isinstance(record.completed_action_items, str):
                completed_action_items = json.loads(record.completed_action_items)
            else:
                completed_action_items = record.completed_action_items
        except (json.JSONDecodeError, TypeError):
            completed_action_items = None
    
    # Parse action_item_due_dates if it's a JSON string
    action_item_due_dates = None
    if record.action_item_due_dates:
        try:
            if isinstance(record.action_item_due_dates, str):
                action_item_due_dates = json.loads(record.action_item_due_dates)
            else:
                action_item_due_dates = record.action_item_due_dates
        except (json.JSONDecodeError, TypeError):
            action_item_due_dates = None
    
    # Parse custom_fields if it's a JSON string
    custom_fields = None
    if record.custom_fields:
        try:
            if isinstance(record.custom_fields, str):
                # Try to parse as JSON, but keep as string if it fails (for backward compatibility)
                try:
                    custom_fields = json.loads(record.custom_fields)
                except json.JSONDecodeError:
                    custom_fields = record.custom_fields  # Keep as string if not valid JSON
            else:
                custom_fields = record.custom_fields
        except (json.JSONDecodeError, TypeError):
            custom_fields = None
    
    # Build regulation response safely
    regulation_response = None
    if regulation_dict:
        try:
            # Ensure all enum values are properly converted
            if regulation_dict.get("safety_category"):
                if isinstance(regulation_dict["safety_category"], str):
                    from app.models import SafetyCategory
                    regulation_dict["safety_category"] = SafetyCategory(regulation_dict["safety_category"])
            if regulation_dict.get("requirement_classification"):
                if isinstance(regulation_dict["requirement_classification"], str):
                    from app.models import RequirementClassification
                    regulation_dict["requirement_classification"] = RequirementClassification(regulation_dict["requirement_classification"])
            if regulation_dict.get("evaluation_type"):
                if isinstance(regulation_dict["evaluation_type"], str):
                    from app.models import EvaluationType
                    regulation_dict["evaluation_type"] = EvaluationType(regulation_dict["evaluation_type"])
            
            regulation_response = schemas.RegulationResponse(**regulation_dict)
        except Exception as e:
            # Log error but don't fail the request
            import traceback
            print(f"⚠️  Erro ao criar RegulationResponse: {e}")
            print(f"   regulation_dict: {regulation_dict}")
            traceback.print_exc()
            regulation_response = None
    
    # Ensure status is properly serialized
    status_value = record.status
    if hasattr(status_value, 'value'):
        status_value = status_value.value
    elif not isinstance(status_value, str):
        status_value = str(status_value)
    
    record_dict = {
        "id": record.id,
        "airport_id": record.airport_id,
        "regulation_id": record.regulation_id,
        "status": status_value,
        "notes": record.notes,
        "docs_score": record.docs_score,
        "tops_score": record.tops_score,
        "weighted_score": record.weighted_score,
        "is_essential_compliant": record.is_essential_compliant,
        "action_items": action_items,
        "completed_action_items": completed_action_items,
        "action_item_due_dates": action_item_due_dates,
        "custom_fields": custom_fields,
        "last_verified": record.last_verified,
        "verified_by": record.verified_by,
        "regulation": regulation_response
    }
    
    try:
        return schemas.ComplianceRecordResponse(**record_dict)
    except Exception as e:
        # Log the full error for debugging
        import traceback
        print(f"❌ Erro ao criar ComplianceRecordResponse: {e}")
        print(f"   record_dict keys: {list(record_dict.keys())}")
        print(f"   record.status type: {type(record.status)}")
        print(f"   record.status value: {record.status}")
        print(f"   status_value: {status_value}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar resposta: {str(e)}"
        )


# ============================================
# Document Attachments Endpoints
# ============================================

# Create uploads directory if it doesn't exist
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

@app.post("/api/compliance/records/{record_id}/documents", response_model=schemas.DocumentAttachmentResponse)
async def upload_document(
    record_id: int,
    file: UploadFile = File(...),
    document_type: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    uploaded_by: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload a document attachment for a compliance record."""
    try:
        # Verify compliance record exists
        record = db.query(ComplianceRecord).filter(ComplianceRecord.id == record_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Compliance record not found")
        
        # Validate file size (max 10MB)
        file_content = await file.read()
        file_size = len(file_content)
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
        
        # Validate file type
        allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx', '.xls', '.xlsx'}
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Create unique filename
        import uuid
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = UPLOADS_DIR / f"record_{record_id}" / unique_filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save file
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Create database record
        db_document = DocumentAttachment(
            compliance_record_id=record_id,
            filename=file.filename,
            file_path=str(file_path),
            file_size=file_size,
            file_type=file.content_type,
            document_type=document_type,
            uploaded_by=uploaded_by,
            description=description
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        return schemas.DocumentAttachmentResponse(
            id=db_document.id,
            compliance_record_id=db_document.compliance_record_id,
            filename=db_document.filename,
            file_path=db_document.file_path,
            file_size=db_document.file_size,
            file_type=db_document.file_type,
            document_type=db_document.document_type,
            description=db_document.description,
            uploaded_at=db_document.uploaded_at,
            uploaded_by=db_document.uploaded_by
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@app.get("/api/compliance/records/{record_id}/documents", response_model=List[schemas.DocumentAttachmentResponse])
def list_documents(record_id: int, db: Session = Depends(get_db)):
    """List all documents for a compliance record."""
    documents = db.query(DocumentAttachment).filter(
        DocumentAttachment.compliance_record_id == record_id
    ).all()
    
    return [
        schemas.DocumentAttachmentResponse(
            id=doc.id,
            compliance_record_id=doc.compliance_record_id,
            filename=doc.filename,
            file_path=doc.file_path,
            file_size=doc.file_size,
            file_type=doc.file_type,
            document_type=doc.document_type,
            description=doc.description,
            uploaded_at=doc.uploaded_at,
            uploaded_by=doc.uploaded_by
        )
        for doc in documents
    ]


@app.get("/api/documents/{document_id}/download")
def download_document(document_id: int, db: Session = Depends(get_db)):
    """Download a document attachment."""
    document = db.query(DocumentAttachment).filter(DocumentAttachment.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="File not found on server")
    
    return FileResponse(
        document.file_path,
        media_type=document.file_type or "application/octet-stream",
        filename=document.filename
    )


@app.delete("/api/documents/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document attachment."""
    document = db.query(DocumentAttachment).filter(DocumentAttachment.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file from filesystem
    if os.path.exists(document.file_path):
        try:
            os.remove(document.file_path)
        except Exception as e:
            print(f"Warning: Could not delete file {document.file_path}: {e}")
    
    # Delete database record
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
