"""
Service for synchronizing airport data with ANAC's official list.

Priority: Características Gerais (completo) > Lista ANAC > cache > banco local.
Características Gerais tem ~6800 aeródromos com todos os dados (RBAC 153/107, RCD, pistas).
"""
import re
import requests
import csv
import json
import io
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from app.models import Airport, AirportCategory, ANACAirport, AirportSize, AirportType
from app.database import SessionLocal


# Cache válido por 7 dias (ANAC atualiza ~a cada 40 dias)
CACHE_MAX_AGE_DAYS = 7

# Códigos de referência válidos (1-4 + A-E) para validação
VALID_REF_CODE = re.compile(r'^[1-4][A-E]$', re.I)


class ANACSyncService:
    """Service for synchronizing airport data with ANAC (fonte oficial preferida)"""

    # URLs de download direto (sistemas.anac.gov.br)
    ANAC_LISTA_URL = "https://sistemas.anac.gov.br/dadosabertos/Aerodromos/Aer%C3%B3dromos%20P%C3%BAblicos/Lista%20de%20aer%C3%B3dromos%20p%C3%BAblicos/AerodromosPublicos.csv"
    ANAC_CARAC_GERAIS_URL = "https://sistemas.anac.gov.br/dadosabertos/Aerodromos/Aer%C3%B3dromos%20P%C3%BAblicos/Caracter%C3%ADsticas%20Gerais/pda_aerodromos_publicos_caracteristicas_gerais.csv"
    ANAC_URLS = [
        ANAC_LISTA_URL,
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

    def _parse_dms_to_decimal(self, dms_str: str) -> Optional[float]:
        """Converte coordenada DMS (ex: 22°54'36,0\"S) para decimal."""
        if not dms_str or not isinstance(dms_str, str):
            return None
        s = dms_str.strip().replace("Â°", "°")  # corrige encoding latin-1
        # Formato: 22°54'36,0"S ou 043°09'45,0"W
        m = re.match(r"(\d+)[°º]\s*(\d+)['′]\s*([\d,]+)[\"″]?\s*([NSOWE])", s, re.I)
        if not m:
            return None
        try:
            deg = int(m.group(1))
            minu = int(m.group(2))
            sec = float(m.group(3).replace(",", "."))
            sign = -1 if m.group(4).upper() in ("S", "W") else 1
            return sign * (deg + minu / 60 + sec / 3600)
        except (ValueError, IndexError):
            return None

    def _download_caracteristicas_gerais(self) -> Dict[str, Dict]:
        """Baixa Características Gerais e retorna dict por Código OACI (para enriquecimento)."""
        try:
            r = requests.get(self.ANAC_CARAC_GERAIS_URL, headers=self.HEADERS, timeout=60)
            r.raise_for_status()
            content = r.content.decode('latin-1')
            reader = csv.DictReader(io.StringIO(content))
            out = {}
            for row in reader:
                code = (row.get('Código OACI') or '').strip().upper()
                if not code or len(code) != 4:
                    continue
                # Classe RBAC 153: 1->I, 2->II, 3->III, 4->IV
                rbac153 = row.get('Classe RBAC 153', '').strip()
                usage = {'1': 'I', '2': 'II', '3': 'III', '4': 'IV'}.get(rbac153)
                # Classe RBAC 107 = AVSEC (AP-0, AP-1, AP-2, AP-3)
                avsec = (row.get('Classe RBAC 107') or '').strip()
                if avsec and avsec.startswith('AP-'):
                    pass
                else:
                    avsec = None
                # Número de pistas: Pista 2 preenchida = 2, senão 1
                p2 = (row.get('Designação (Pista 2)') or '').strip()
                runways = 2 if p2 and len(p2) > 2 else 1
                out[code] = {
                    'usage_class': usage,
                    'avsec_classification': avsec or None,
                    'number_of_runways': runways,
                }
            return out
        except Exception as e:
            print(f"Aviso: Características Gerais indisponível: {e}")
            return {}

    def _normalize_caracteristicas_row(self, row: Dict) -> Optional[Dict]:
        """Normaliza uma linha do CSV Características Gerais para o schema do banco."""
        try:
            code = (row.get('Código OACI') or '').strip().upper()
            if not code or len(code) != 4:
                return None
            name = (row.get('Nome') or '').strip()
            if not name:
                return None
            # Tipo de Uso: Público -> usage I-IV; Privado -> PRIVADO
            tipo_uso = (row.get('Tipo de Uso') or '').strip()
            rbac153 = row.get('Classe RBAC 153', '').strip()
            if tipo_uso and 'rivado' in tipo_uso.lower():
                usage_class = 'PRIVADO'
            else:
                usage_class = {'1': 'I', '2': 'II', '3': 'III', '4': 'IV'}.get(rbac153)
            avsec = (row.get('Classe RBAC 107') or '').strip()
            avsec = avsec if avsec and avsec.startswith('AP-') else None
            p2 = (row.get('Designação (Pista 2)') or '').strip()
            runways = 2 if p2 and len(p2) > 2 else 1
            # Código de referência: Aeronave Crítica (Pista 1) ou (Pista 2) - ex: 4E, 3C
            ref1 = (row.get('Aeronave Crítica (Pista 1)') or '').strip().upper()
            ref2 = (row.get('Aeronave Crítica (Pista 2)') or '').strip().upper()
            refs = [r for r in (ref1, ref2) if r and VALID_REF_CODE.match(r)]
            reference_code = max(refs, key=lambda x: (int(x[0]), x[1])) if refs else None
            # Coordenadas: DMS ou decimal
            lat_str = (row.get('Latitude') or '').strip()
            lon_str = (row.get('Longitude') or '').strip()
            lat = self._parse_float(lat_str) or self._parse_dms_to_decimal(lat_str)
            lon = self._parse_float(lon_str) or self._parse_dms_to_decimal(lon_str)
            city = (row.get('Município Servido') or row.get('Município') or '').strip() or None
            state = (row.get('UF') or '').strip().upper() or None
            status = (row.get('Situação') or '').strip() or None
            return {
                'code': code,
                'name': name,
                'reference_code': reference_code,
                'category': None,
                'city': city,
                'state': state,
                'latitude': lat,
                'longitude': lon,
                'iata_code': None,
                'status': status,
                'usage_class': usage_class,
                'avsec_classification': avsec,
                'aircraft_size_category': self._ref_to_aircraft_size(reference_code),
                'number_of_runways': runways,
            }
        except Exception as e:
            print(f"⚠️ Erro ao normalizar Características: {e}")
            return None

    def _ref_to_aircraft_size(self, ref: Optional[str]) -> Optional[str]:
        """Infere aircraft_size_category a partir do reference_code."""
        if not ref or len(ref) < 2:
            return None
        lt = ref[-1].upper()
        if lt in ('A', 'B'):
            return 'A/B'
        if lt == 'C':
            return 'C'
        if lt in ('D', 'E'):
            return 'D'
        return None

    def download_from_caracteristicas_gerais(self) -> Optional[List[Dict]]:
        """
        Baixa a lista COMPLETA de aeródromos do CSV Características Gerais da ANAC.
        Contém ~6800 aeródromos com nome, coordenadas, RBAC 153/107, RCD, pistas.
        """
        try:
            r = requests.get(self.ANAC_CARAC_GERAIS_URL, headers=self.HEADERS, timeout=120)
            r.raise_for_status()
            for enc in ('utf-8', 'latin-1', 'cp1252'):
                try:
                    content = r.content.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                content = r.content.decode('latin-1', errors='replace')
            reader = csv.DictReader(io.StringIO(content))
            airports = []
            for row in reader:
                a = self._normalize_caracteristicas_row(row)
                if a:
                    airports.append(a)
            if len(airports) < 100:
                return None
            from app.seed_data import ANAC_AIRPORTS_BOOTSTRAP
            bootstrap_by_code = {b['code']: b for b in ANAC_AIRPORTS_BOOTSTRAP}
            for a in airports:
                code = a['code']
                if code in bootstrap_by_code:
                    b = bootstrap_by_code[code]
                    if not a.get('reference_code') and b.get('reference_code'):
                        a['reference_code'] = b['reference_code']
                        a['aircraft_size_category'] = self._ref_to_aircraft_size(a['reference_code'])
                    if not a.get('category') and b.get('category'):
                        a['category'] = b['category']
                    if not a.get('usage_class') and b.get('usage_class'):
                        a['usage_class'] = b['usage_class']
                    if not a.get('avsec_classification') and b.get('avsec_classification'):
                        a['avsec_classification'] = b['avsec_classification']
            self._save_cache(airports)
            if self.db:
                self._save_to_anac_airports_table(airports)
            return airports
        except Exception as e:
            print(f"Erro ao baixar Características Gerais: {e}")
            return None

    def download_anac_data(self) -> Optional[List[Dict]]:
        """
        Baixa e parseia dados da ANAC (fonte oficial).
        Prioridade: Características Gerais (lista completa ~6800) > Lista ANAC (enriquecida).
        """
        # 1. Tentar Características Gerais primeiro (lista completa com todos os dados)
        data = self.download_from_caracteristicas_gerais()
        if data:
            return data
        # 2. Fallback: Lista ANAC + enriquecimento com Características Gerais
        for url in self.ANAC_URLS:
            try:
                response = requests.get(url, headers=self.HEADERS, timeout=30)
                response.raise_for_status()
                for enc in ('latin-1', 'utf-8-sig', 'utf-8'):
                    try:
                        content = response.content.decode(enc)
                        break
                    except UnicodeDecodeError:
                        continue
                if content.strip().startswith('<!') or '<html' in content.lower()[:200]:
                    continue
                lines = content.strip().split('\n')
                if lines and 'Atualizado em' in lines[0]:
                    content = '\n'.join(lines[1:])
                for delim in (';', ','):
                    try:
                        csv_reader = csv.DictReader(io.StringIO(content), delimiter=delim)
                        airports = [self._normalize_anac_data(row) for row in csv_reader]
                        airports = [a for a in airports if a]
                        if len(airports) >= 10:
                            # Enriquecer com Características Gerais
                            carac = self._download_caracteristicas_gerais()
                            from app.seed_data import ANAC_AIRPORTS_BOOTSTRAP
                            bootstrap_by_code = {a['code']: a for a in ANAC_AIRPORTS_BOOTSTRAP}
                            for a in airports:
                                code = a['code']
                                a.setdefault('number_of_runways', 1)
                                if code in carac:
                                    a.setdefault('usage_class', carac[code]['usage_class'])
                                    a.setdefault('avsec_classification', carac[code]['avsec_classification'])
                                    a['number_of_runways'] = carac[code]['number_of_runways']
                                if code in bootstrap_by_code:
                                    b = bootstrap_by_code[code]
                                    if not a.get('reference_code') and b.get('reference_code'):
                                        a['reference_code'] = b['reference_code']
                                    if not a.get('category') and b.get('category'):
                                        a['category'] = b['category']
                                    if not a.get('usage_class') and b.get('usage_class'):
                                        a['usage_class'] = b['usage_class']
                                    if not a.get('avsec_classification') and b.get('avsec_classification'):
                                        a['avsec_classification'] = b['avsec_classification']
                                    if (not a.get('number_of_runways') or a.get('number_of_runways') == 1) and b.get('number_of_runways'):
                                        a['number_of_runways'] = b['number_of_runways']
                                # Inferir aircraft_size_category de reference_code
                                if a.get('reference_code') and not a.get('aircraft_size_category'):
                                    ref = a['reference_code'].upper()
                                    if len(ref) >= 2:
                                        lt = ref[-1]
                                        a['aircraft_size_category'] = 'A/B' if lt in ('A','B') else 'C' if lt == 'C' else 'D'
                            self._save_cache(airports)
                            if self.db:
                                self._save_to_anac_airports_table(airports)
                            return airports
                    except Exception:
                        continue
            except requests.RequestException as e:
                print(f"Erro ao baixar ANAC ({url[:60]}...): {e}")
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
                    'usage_class': data.get('usage_class'),
                    'avsec_classification': data.get('avsec_classification'),
                    'aircraft_size_category': data.get('aircraft_size_category'),
                    'number_of_runways': data.get('number_of_runways', 1),
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
            'usage_class': getattr(row, 'usage_class', None),
            'avsec_classification': getattr(row, 'avsec_classification', None),
            'aircraft_size_category': getattr(row, 'aircraft_size_category', None),
            'number_of_runways': getattr(row, 'number_of_runways', None) or 1,
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
            code = self._get_row_val(row, 'ICAO', 'Código ICAO', 'CÓDIGO OACI', 'Código OACI', 'codigo_oaci', 'ICAO Code').upper()
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
                'latitude': self._parse_float(self._get_row_val(row, 'LATGEOPOINT', 'Latitude', 'LATITUDE', 'latitude', 'Coordenada')),
                'longitude': self._parse_float(self._get_row_val(row, 'LONGEOPOINT', 'Longitude', 'LONGITUDE', 'longitude')),
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
        """Update airport with ANAC data and return list of changed fields. Propagates usage_class, size, annual_passengers."""
        changes = []

        # Update name if different
        if anac_data.get('name') and airport.name != anac_data['name']:
            if not dry_run:
                airport.name = anac_data['name']
            changes.append(f"name: '{airport.name}' -> '{anac_data['name']}'")

        # Update usage_class and derived fields (size, annual_passengers) - critical for SME/COE/PCM
        usage_class = anac_data.get('usage_class')
        if usage_class is not None:
            if str(airport.usage_class or '') != str(usage_class):
                if not dry_run:
                    airport.usage_class = usage_class
                    size, annual_passengers = self._infer_from_usage_class(usage_class)
                    airport.size = size
                    airport.annual_passengers = annual_passengers
                changes.append(f"usage_class: {airport.usage_class} -> {usage_class} (size/annual_passengers updated)")
            elif not airport.annual_passengers and usage_class:
                # Airport has usage_class but missing annual_passengers - backfill
                if not dry_run:
                    _, annual_passengers = self._infer_from_usage_class(usage_class)
                    airport.annual_passengers = annual_passengers
                changes.append("annual_passengers: backfilled from usage_class")

        # Update avsec_classification
        if anac_data.get('avsec_classification') is not None and airport.avsec_classification != anac_data['avsec_classification']:
            if not dry_run:
                airport.avsec_classification = anac_data['avsec_classification']
            changes.append(f"avsec_classification: {airport.avsec_classification} -> {anac_data['avsec_classification']}")

        # Update category if provided and different (fallback when usage_class not available)
        if anac_data.get('category'):
            try:
                category_key = f"CAT_{anac_data['category']}"
                category_enum = AirportCategory[category_key]
                if airport.category != category_enum:
                    if not dry_run:
                        airport.category = category_enum
                    changes.append(f"category: {airport.category.value if airport.category else None} -> {category_enum.value}")
                # If no usage_class, infer size from category
                if not usage_class and anac_data.get('category'):
                    new_size = self._infer_size_from_category(anac_data['category'])
                    if airport.size != new_size:
                        if not dry_run:
                            airport.size = new_size
                        changes.append(f"size (from category): {airport.size} -> {new_size}")
            except (KeyError, AttributeError):
                pass

        # Update reference_code, aircraft_size_category
        if anac_data.get('reference_code') is not None and airport.reference_code != anac_data['reference_code']:
            if not dry_run:
                airport.reference_code = anac_data['reference_code']
            changes.append(f"reference_code: '{airport.reference_code}' -> '{anac_data['reference_code']}'")
        if anac_data.get('aircraft_size_category') is not None and airport.aircraft_size_category != anac_data['aircraft_size_category']:
            if not dry_run:
                airport.aircraft_size_category = anac_data['aircraft_size_category']
            changes.append(f"aircraft_size_category: {airport.aircraft_size_category} -> {anac_data['aircraft_size_category']}")

        # Update number_of_runways, cidade, estado, coordinates
        if anac_data.get('number_of_runways') is not None and airport.number_of_runways != anac_data['number_of_runways']:
            if not dry_run:
                airport.number_of_runways = anac_data['number_of_runways']
            changes.append(f"number_of_runways: {airport.number_of_runways} -> {anac_data['number_of_runways']}")
        if anac_data.get('city') is not None and airport.cidade != anac_data['city']:
            if not dry_run:
                airport.cidade = anac_data['city']
            changes.append(f"cidade: {airport.cidade} -> {anac_data['city']}")
        if anac_data.get('state') is not None and airport.estado != anac_data['state']:
            if not dry_run:
                airport.estado = anac_data['state']
            changes.append(f"estado: {airport.estado} -> {anac_data['state']}")
        if anac_data.get('latitude') is not None and airport.latitude != anac_data['latitude']:
            if not dry_run:
                airport.latitude = anac_data['latitude']
            changes.append("latitude updated")
        if anac_data.get('longitude') is not None and airport.longitude != anac_data['longitude']:
            if not dry_run:
                airport.longitude = anac_data['longitude']
            changes.append("longitude updated")

        # Update sync metadata
        if not dry_run:
            airport.data_sincronizacao_anac = datetime.utcnow()
            airport.origem_dados = 'anac'
            if anac_data.get('status'):
                airport.status_operacional = anac_data['status']

        return changes
    
    def _create_airport(self, anac_data: Dict) -> Optional[Airport]:
        """Create a new airport from ANAC data. Uses usage_class (RBAC 153) for size/annual_passengers."""
        try:
            usage_class = anac_data.get('usage_class')
            if usage_class:
                size, annual_passengers = self._infer_from_usage_class(usage_class)
            else:
                size = self._infer_size_from_category(anac_data.get('category'))
                annual_passengers = None

            airport_type = AirportType.COMMERCIAL

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
                annual_passengers=annual_passengers,
                category=category_enum,
                reference_code=anac_data.get('reference_code'),
                usage_class=anac_data.get('usage_class'),
                avsec_classification=anac_data.get('avsec_classification'),
                aircraft_size_category=anac_data.get('aircraft_size_category'),
                number_of_runways=anac_data.get('number_of_runways') or 1,
                cidade=anac_data.get('city'),
                estado=anac_data.get('state'),
                latitude=anac_data.get('latitude'),
                longitude=anac_data.get('longitude'),
                codigo_iata=anac_data.get('iata_code'),
                data_sincronizacao_anac=datetime.utcnow(),
                origem_dados='anac',
                status_operacional=anac_data.get('status'),
            )

            return airport

        except Exception as e:
            print(f"⚠️  Erro ao criar aeroporto: {e}")
            return None
    
    def _infer_from_usage_class(self, usage_class: Optional[str]) -> Tuple[AirportSize, int]:
        """
        Infer size and annual_passengers from usage_class (RBAC 153).
        Same logic as main.py create_airport/update_airport.
        """
        if not usage_class:
            return AirportSize.SMALL, 100000
        uc = str(usage_class).strip().upper()
        if uc == 'PRIVADO':
            return AirportSize.SMALL, 0
        if uc == 'I':
            return AirportSize.SMALL, 100000
        if uc == 'II':
            return AirportSize.MEDIUM, 600000
        if uc == 'III':
            return AirportSize.LARGE, 3000000
        if uc == 'IV':
            return AirportSize.INTERNATIONAL, 10000000
        return AirportSize.SMALL, 100000

    def _infer_size_from_category(self, category: Optional[str]) -> AirportSize:
        """Infer airport size from category (fallback when usage_class is not available)"""
        if not category:
            return AirportSize.SMALL
        try:
            category_num = int(category.replace('C', '')) if category.replace('C', '').isdigit() else 1
        except (ValueError, AttributeError):
            return AirportSize.SMALL
        if category_num <= 2:
            return AirportSize.SMALL
        elif category_num <= 4:
            return AirportSize.MEDIUM
        elif category_num <= 6:
            return AirportSize.LARGE
        else:
            return AirportSize.INTERNATIONAL
    
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
