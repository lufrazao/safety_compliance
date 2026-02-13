"""
Service for synchronizing airport data with ANAC's official list.

Priority: ANAC ao vivo > cache ANAC > banco local.
Quando a ANAC responde, os dados são salvos em cache para uso offline.
"""
import requests
import csv
import json
import io
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from app.models import Airport, AirportCategory, ANACAirport
from app.database import SessionLocal


# Cache válido por 7 dias (ANAC atualiza ~a cada 40 dias)
CACHE_MAX_AGE_DAYS = 7


class ANACSyncService:
    """Service for synchronizing airport data with ANAC (fonte oficial preferida)"""

    # URLs oficiais ANAC - lista de aeródromos públicos (formato CSV/JSON)
    ANAC_URLS = [
        "https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/lista-de-aerodromos-publicos-v2/lista-de-aerodromos-publicos-v2-formato-csv-json",
        "https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/lista-de-aerodromos-publicos-v2",
    ]

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/csv,application/csv,text/plain,*/*;q=0.9",
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    }

    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
        base_dir = Path(__file__).resolve().parent.parent.parent
        self._cache_path = base_dir / "data" / "anac_airports_cache.json"

    def _get_cache_path(self) -> Path:
        self._cache_path.parent.mkdir(parents=True, exist_ok=True)
        return self._cache_path

    def _load_cache(self, max_age_days: int = CACHE_MAX_AGE_DAYS) -> Optional[List[Dict]]:
        """Carrega cache ANAC se existir e não estiver expirado."""
        try:
            path = self._get_cache_path()
            if not path.exists():
                return None
            mtime = path.stat().st_mtime
            age_days = (datetime.now().timestamp() - mtime) / 86400
            if age_days > max_age_days:
                return None
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("airports") or None
        except Exception:
            return None

    def _save_cache(self, airports: List[Dict]) -> None:
        """Salva dados ANAC no cache para uso offline."""
        try:
            path = self._get_cache_path()
            with open(path, "w", encoding="utf-8") as f:
                json.dump({
                    "airports": airports,
                    "updated_at": datetime.utcnow().isoformat(),
                    "source": "anac",
                }, f, ensure_ascii=False)
        except Exception as e:
            print(f"Aviso: não foi possível salvar cache ANAC: {e}")

    def download_anac_data(self) -> Optional[List[Dict]]:
        """
        Baixa e parseia dados da ANAC (fonte oficial).
        Se conseguir, salva em cache.
        """
        for url in self.ANAC_URLS:
            try:
                response = requests.get(url, headers=self.HEADERS, timeout=30)
                response.raise_for_status()
                content = response.content.decode('utf-8-sig')
                if content.strip().startswith('<!') or '<html' in content.lower()[:200]:
                    continue
                for delim in (';', ','):
                    try:
                        csv_reader = csv.DictReader(io.StringIO(content), delimiter=delim)
                        airports = [self._normalize_anac_data(row) for row in csv_reader]
                        airports = [a for a in airports if a]
                        if len(airports) >= 10:
                            self._save_cache(airports)
                            self._save_to_anac_airports_table(airports)
                            return airports
                    except Exception:
                        continue
            except requests.RequestException as e:
                print(f"Erro ao baixar ANAC ({url}): {e}")
            except Exception as e:
                print(f"Erro ao processar ANAC: {e}")
        return None

    def _save_to_anac_airports_table(self, airports: List[Dict]) -> int:
        """Salva/atualiza aeroportos na tabela anac_airports."""
        count = 0
        try:
            for data in airports:
                code = (data.get('code') or '').upper()
                if not code or len(code) != 4:
                    continue
                existing = self.db.query(ANACAirport).filter(ANACAirport.code == code).first()
                row = {
                    'code': code,
                    'name': data.get('name') or '',
                    'reference_code': data.get('reference_code'),
                    'category': data.get('category'),
                    'city': data.get('city'),
                    'state': data.get('state'),
                    'latitude': data.get('latitude'),
                    'longitude': data.get('longitude'),
                    'iata_code': data.get('iata_code'),
                    'status': data.get('status'),
                }
                if existing:
                    for k, v in row.items():
                        setattr(existing, k, v)
                    existing.updated_at = datetime.utcnow()
                else:
                    self.db.add(ANACAirport(**row))
                count += 1
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao salvar em anac_airports: {e}")
        return count

    def get_from_anac_airports_table(self, icao_code: str) -> Optional[Dict]:
        """Busca aeroporto na tabela anac_airports (cache local)."""
        row = self.db.query(ANACAirport).filter(ANACAirport.code == icao_code.upper()).first()
        if not row:
            return None
        return {
            'code': row.code,
            'name': row.name,
            'reference_code': row.reference_code,
            'category': row.category,
            'city': row.city,
            'state': row.state,
            'latitude': row.latitude,
            'longitude': row.longitude,
            'iata_code': row.iata_code,
            'status': row.status,
        }

    def get_anac_data(self, use_cache_if_live_fails: bool = True) -> Tuple[Optional[List[Dict]], str]:
        """
        Obtém dados ANAC: tenta download ao vivo; se falhar, usa cache.
        Retorna (dados, origem) onde origem é 'anac' (ao vivo) ou 'anac_cache'.
        """
        data = self.download_anac_data()
        if data:
            return data, "anac"
        if use_cache_if_live_fails:
            cached = self._load_cache()
            if cached:
                return cached, "anac_cache"
        return None, ""
    
    def _get_row_val(self, row: Dict, *keys: str) -> str:
        """Obtém valor da linha tentando várias chaves (ANAC usa nomes variados)."""
        for k in keys:
            v = row.get(k, '')
            if v and str(v).strip():
                return str(v).strip()
        return row.get(keys[0], '') if keys else ''

    def _normalize_anac_data(self, row: Dict) -> Optional[Dict]:
        """
        Normalize ANAC data to match our database schema.
        Suporta múltiplos nomes de colunas (ANAC V2 usa CÓDIGO OACI, NOME, etc.).
        """
        try:
            name = self._get_row_val(row, 'Nome', 'NOME', 'Aeródromo', 'Nome do Aeródromo', 'nome')
            code = self._get_row_val(row, 'ICAO', 'Código ICAO', 'CÓDIGO OACI', 'codigo_oaci', 'ICAO Code').upper()
            reference_code = self._get_row_val(row, 'Código de Referência', 'Código Referência', 'REFERÊNCIA', 'codigo_referencia') or None
            if not reference_code:
                # Categoria 1C-9C pode ser usada como referência para pista (ex: 4C)
                cat = self._parse_category(row)
                if cat:
                    reference_code = cat
            category = self._parse_category(row)
            normalized = {
                'name': name,
                'code': code,
                'iata_code': self._get_row_val(row, 'IATA', 'Código IATA', 'codigo_iata').upper() or None,
                'category': category,
                'reference_code': reference_code,
                'city': self._get_row_val(row, 'Cidade', 'Município', 'MUNICÍPIO', 'Município Atendido') or None,
                'state': self._get_row_val(row, 'Estado', 'UF', 'uf').upper() or None,
                'latitude': self._parse_float(self._get_row_val(row, 'Latitude', 'LATITUDE', 'latitude', 'Coordenada')),
                'longitude': self._parse_float(self._get_row_val(row, 'Longitude', 'LONGITUDE', 'longitude')),
                'status': self._get_row_val(row, 'Status', 'Situação', 'OPERAÇÃO', 'Operação') or None,
            }
            
            # Validate required fields
            if not normalized['code'] or len(normalized['code']) != 4:
                return None  # Invalid ICAO code
            
            if not normalized['name']:
                return None  # Missing name
            
            return normalized
            
        except Exception as e:
            print(f"⚠️  Erro ao normalizar dados: {e}")
            return None
    
    def _parse_category(self, row: Dict) -> Optional[str]:
        """Parse and validate airport category from ANAC data (1C-9C)"""
        category = self._get_row_val(row, 'Categoria', 'Categoria do Aeródromo', 'CATEGORIA', 'Tipo')
        category = category.upper().replace(' ', '') if category else ''
        if category in ['1C', '2C', '3C', '4C', '5C', '6C', '7C', '8C', '9C']:
            return category
        return None
    
    def _parse_float(self, value: str) -> Optional[float]:
        """Parse float value, handling common formatting issues"""
        if not value:
            return None
        try:
            # Remove common formatting characters
            cleaned = value.replace(',', '.').strip()
            return float(cleaned)
        except (ValueError, AttributeError):
            return None
    
    def sync_airports(self, anac_data: List[Dict], dry_run: bool = False) -> Dict:
        """
        Synchronize airports with ANAC data.
        
        Args:
            anac_data: List of normalized airport data from ANAC
            dry_run: If True, don't actually update the database
            
        Returns:
            Dictionary with sync results
        """
        results = {
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0,
            'changes': []
        }
        
        if not anac_data:
            return results
        
        try:
            for airport_data in anac_data:
                try:
                    # Find existing airport by ICAO code
                    existing = self.db.query(Airport).filter(
                        Airport.code == airport_data['code']
                    ).first()
                    
                    if existing:
                        # Update existing airport
                        changes = self._update_airport(existing, airport_data, dry_run)
                        if changes:
                            results['updated'] += 1
                            results['changes'].append({
                                'airport_id': existing.id,
                                'code': existing.code,
                                'action': 'updated',
                                'changes': changes
                            })
                        else:
                            results['skipped'] += 1
                    else:
                        # Create new airport
                        if not dry_run:
                            new_airport = self._create_airport(airport_data)
                            if new_airport:
                                self.db.add(new_airport)
                                results['created'] += 1
                                results['changes'].append({
                                    'code': airport_data['code'],
                                    'action': 'created',
                                    'name': airport_data['name']
                                })
                        else:
                            results['created'] += 1
                            
                except Exception as e:
                    print(f"⚠️  Erro ao processar aeroporto {airport_data.get('code', 'UNKNOWN')}: {e}")
                    results['errors'] += 1
            
            if not dry_run:
                self.db.commit()
            
            return results
            
        except Exception as e:
            if not dry_run:
                self.db.rollback()
            print(f"❌ Erro durante sincronização: {e}")
            results['errors'] += 1
            return results
    
    def _update_airport(self, airport: Airport, anac_data: Dict, dry_run: bool) -> List[str]:
        """Update airport with ANAC data and return list of changed fields"""
        changes = []
        
        # Update name if different
        if anac_data.get('name') and airport.name != anac_data['name']:
            if not dry_run:
                airport.name = anac_data['name']
            changes.append(f"name: '{airport.name}' -> '{anac_data['name']}'")
        
        # Update category if provided and different
        if anac_data.get('category'):
            try:
                # Map category string (e.g., "3C") to enum (e.g., AirportCategory.CAT_3C)
                category_key = f"CAT_{anac_data['category']}"
                category_enum = AirportCategory[category_key]
                if airport.category != category_enum:
                    if not dry_run:
                        airport.category = category_enum
                    changes.append(f"category: {airport.category.value if airport.category else None} -> {category_enum.value}")
            except (KeyError, AttributeError) as e:
                print(f"⚠️  Erro ao mapear categoria {anac_data.get('category')}: {e}")
                pass
        
        # Update reference_code if provided and different
        if anac_data.get('reference_code') and airport.reference_code != anac_data['reference_code']:
            if not dry_run:
                airport.reference_code = anac_data['reference_code']
            changes.append(f"reference_code: '{airport.reference_code}' -> '{anac_data['reference_code']}'")
        
        # Update sync metadata
        if not dry_run:
            airport.data_sincronizacao_anac = datetime.utcnow()
            airport.origem_dados = 'anac'
            if anac_data.get('status'):
                airport.status_operacional = anac_data['status']
        
        return changes
    
    def _create_airport(self, anac_data: Dict) -> Optional[Airport]:
        """Create a new airport from ANAC data"""
        try:
            # Determine size based on category (fallback logic)
            size = self._infer_size_from_category(anac_data.get('category'))
            
            # Determine airport type (default to commercial)
            airport_type = 'commercial'  # Default, can be enhanced with more logic
            
            category_enum = None
            if anac_data.get('category'):
                try:
                    category_key = f"CAT_{anac_data['category']}"
                    category_enum = AirportCategory[category_key]
                except KeyError:
                    pass
            
            airport = Airport(
                name=anac_data['name'],
                code=anac_data['code'],
                size=size,
                airport_type=airport_type,
                category=category_enum,
                reference_code=anac_data.get('reference_code'),
                data_sincronizacao_anac=datetime.utcnow(),
                origem_dados='anac',
                status_operacional=anac_data.get('status'),
            )
            
            return airport
            
        except Exception as e:
            print(f"⚠️  Erro ao criar aeroporto: {e}")
            return None
    
    def _infer_size_from_category(self, category: Optional[str]) -> str:
        """Infer airport size from category"""
        if not category:
            return 'small'  # Default
        
        category_num = int(category.replace('C', '')) if category.replace('C', '').isdigit() else 1
        
        if category_num <= 2:
            return 'small'
        elif category_num <= 4:
            return 'medium'
        elif category_num <= 6:
            return 'large'
        else:
            return 'international'
    
    def detect_changes(self, airport: Airport, anac_data: Dict) -> List[Dict]:
        """Detect changes between local airport and ANAC data"""
        changes = []
        
        if anac_data.get('name') and airport.name != anac_data['name']:
            changes.append({
                'field': 'name',
                'old': airport.name,
                'new': anac_data['name']
            })
        
        if anac_data.get('category'):
            try:
                category_key = f"CAT_{anac_data['category']}"
                category_enum = AirportCategory[category_key]
                if airport.category != category_enum:
                    changes.append({
                        'field': 'category',
                        'old': airport.category.value if airport.category else None,
                        'new': category_enum.value
                    })
            except (KeyError, AttributeError):
                pass
        
        return changes
    
    def __del__(self):
        """Close database session on cleanup"""
        if self.db:
            self.db.close()
