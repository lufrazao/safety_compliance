"""
Scraper de dados de aeródromos do eAIS (AISWEB/DECEA).
Fonte oficial: https://aisweb.decea.mil.br/?codigo=XXXX&i=aerodromos

Extrai dados para cadastro e verificação de conformidade (RBAC-153/154).
NÃO usa ANAC - os dados vêm exclusivamente do eAIS.
"""
import logging
import re
import requests
from typing import Optional, Dict

logger = logging.getLogger(__name__)

EAIS_URL = "https://aisweb.decea.mil.br/?codigo={icao}&i=aerodromos"
HTML_PREVIEW_LENGTH = 3000  # caracteres para debug
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9",
}
VALID_REF = re.compile(r"^[1-4][A-E]$", re.I)


def _parse_coords(match) -> tuple:
    """Converte DD MM SS N/S e DDD MM SS E/W para decimal."""
    d, mn, s, ns = int(match.group(1)), int(match.group(2)), float(match.group(3)), match.group(4)
    lat = (d + mn / 60 + s / 3600) * (-1 if ns == "S" else 1)
    d, mn, s, ew = int(match.group(5)), int(match.group(6)), float(match.group(7)), match.group(8)
    lon = (d + mn / 60 + s / 3600) * (-1 if ew == "W" else 1)
    return lat, lon


def _infer_usage_avsec_from_cat(cat: int) -> tuple:
    """Infere usage_class e avsec a partir da CAT CIVIL (fire category)."""
    if cat >= 9:
        return "IV", "AP-3"
    if cat >= 7:
        return "IV", "AP-3"
    if cat >= 5:
        return "III", "AP-2"
    if cat >= 3:
        return "II", "AP-1"
    return "I", "AP-1"


def _infer_rcd_from_tora(tora_m: int) -> Optional[str]:
    """Infere RCD a partir do comprimento da pista (TORA em metros).
    Conservador: sem largura não inferir 4E - muitas pistas 2000-2600m são 4C (45m)."""
    if tora_m >= 3000:
        return "4E"  # Pistas longas geralmente têm largura adequada
    if tora_m >= 1800:
        return "4C"  # Conservador: 4C em vez de 4E (evita sobrestimar)
    if tora_m >= 1200:
        return "4C"
    if tora_m >= 900:
        return "3C"
    if tora_m >= 800:
        return "3B"
    return None


def fetch_eais_airport(icao_code: str) -> Optional[Dict]:
    """
    Busca dados do aeródromo no eAIS (AISWEB) - ÚNICA FONTE.
    Retorna dict com todos os campos para cadastro e conformidade.
    """
    icao = icao_code.upper().strip()
    if len(icao) != 4 or not icao.isalpha():
        return None
    try:
        r = requests.get(EAIS_URL.format(icao=icao), headers=HEADERS, timeout=20)
        r.raise_for_status()
        text = r.text
        if icao not in text and "Aeródromo" not in text[:3000]:
            logger.warning(
                "eAIS: página inválida ou formato inesperado para %s (código ou 'Aeródromo' não encontrado no conteúdo)",
                icao,
            )
            return None
        result = {"code": icao, "source": "eais"}

        # Nome e código do h1
        m = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.DOTALL)
        if m:
            h1 = re.sub(r"\s+", " ", m.group(1)).strip()
            name_match = re.search(r"(.+?)\s*\(\s*" + icao + r"\s*\)", h1)
            result["name"] = name_match.group(1).strip() if name_match else h1.split("(")[0].strip()[:80]

        # Estado: <span title="Estado">SP</span> ou extraído do padrão cidade/UF
        m = re.search(r'<span title="Estado">([A-Z]{2})</span>', text)
        result["state"] = m.group(1) if m else None
        # Cidade: formatos do eAIS "Cidade/UF", "Cidade - UF", "Cidade, UF"
        city_match = re.search(
            r"([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\s\-]{2,40})/\s*([A-Z]{2})\s*(?:&nbsp;|</span>|[\s<])",
            text,
        )
        if city_match:
            city = city_match.group(1).strip()
            if not any(c.isdigit() for c in city) and len(city) > 2:
                result["city"] = city
            if not result.get("state"):
                result["state"] = city_match.group(2)
        # Fallback: "Cidade - UF" ou "Cidade, UF" (ex.: em tabelas)
        if not result.get("city"):
            for pat in [
                r"([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\s\-]{2,40})\s*[-–]\s*([A-Z]{2})\b",
                r"([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\s\-]{2,40}),\s*([A-Z]{2})\b",
            ]:
                m = re.search(pat, text)
                if m:
                    city = m.group(1).strip()
                    if not any(c.isdigit() for c in city) and len(city) > 2:
                        result["city"] = city
                        if not result.get("state"):
                            result["state"] = m.group(2)
                    break

        # Coordenadas: DD MM SS N/S e DDD MM SS E/W (formato principal do eAIS)
        coord_match = re.search(
            r"(\d{1,2})\s+(\d{1,2})\s+(\d{1,2})([NS])/(\d{1,3})\s+(\d{1,2})\s+(\d{1,2})([EW])",
            text,
        )
        if coord_match:
            result["latitude"], result["longitude"] = _parse_coords(coord_match)
        else:
            # Fallback: formato graus-minutos "23°26'08"S" ou decimal "-23.4356"
            deg_match = re.search(
                r"(\d{1,2})[°º]\s*(\d{1,2})['′]?\s*(\d{1,2}(?:[.,]\d+)?)[\"″]?\s*([NS])\s*[/\s,]\s*(\d{1,3})[°º]?\s*(\d{1,2})['′]?\s*(\d{1,2}(?:[.,]\d+)?)[\"″]?\s*([EW])",
                text,
            )
            if deg_match:
                try:
                    lat = (
                        int(deg_match.group(1))
                        + int(deg_match.group(2)) / 60
                        + float(deg_match.group(3).replace(",", ".")) / 3600
                    ) * (-1 if deg_match.group(4) == "S" else 1)
                    lon = (
                        int(deg_match.group(5))
                        + int(deg_match.group(6)) / 60
                        + float(deg_match.group(7).replace(",", ".")) / 3600
                    ) * (-1 if deg_match.group(8) == "W" else 1)
                    result["latitude"], result["longitude"] = lat, lon
                except (ValueError, IndexError):
                    pass

        # CAT CIVIL (categoria contraincêndio 1-10) - crítico para RBAC-153/SESCINC
        # Formato oficial eAIS/ROTAER: "RFFS - CAT CIVIL - 7" ou "CAT CIVIL - 10" (tabela COMPL)
        # Priorizar padrões explícitos; evitar "CAT 1" de outros contextos (ex: categoria 1)
        fire_category = None
        for pat in [
            r"CAT\s+CIVIL\s*[-–]\s*(\d+)",  # Formato exato: "CAT CIVIL - 7" (hífen ou en-dash)
            r"CAT\s+CIVIL\s*:\s*(\d+)",
            r"CAT\s+CIVIL\s+(\d+)\b",
            r"RFFS\s*[-–]\s*CAT\s+CIVIL\s*[-–]\s*(\d+)",  # Formato ROTAER COMPL
            r"Categoria\s+Contraincêndio\s*[:\-]\s*(\d+)",
        ]:
            cat_match = re.search(pat, text, re.I)
            if cat_match and cat_match.group(1).isdigit():
                val = int(cat_match.group(1))
                if 1 <= val <= 10:
                    fire_category = val
                    break
        if fire_category:
            result["fire_category"] = fire_category
            result["usage_class"], result["avsec_classification"] = _infer_usage_avsec_from_cat(fire_category)

        # RCD - prioridade: explícito no texto > tabela RWY > inferência TORA
        rcd = None
        rcd_source = None
        for pat, src in [
            (r"compatíveis com o RCD\s+([1-4][A-E])", "texto"),
            (r"RCD\s+([1-4][A-E])", "texto"),
            (r"código\s+([1-4][A-E])\b", "texto"),
            (r"([1-4][A-E])\s+ou inferior", "texto"),
            (r"\b([1-4][A-E])\s*[-(]?(?:RCD|referência)", "texto"),
        ]:
            m = re.search(pat, text, re.I)
            if m:
                rcd = m.group(1).upper()
                rcd_source = src
                break
        # RCD no formato "RWY 02L/20R 3C" ou "RWY 02R/20L 4C"
        if not rcd:
            rcd_matches = re.findall(r"RWY\s+[\d/]+[LR]?\s+([1-4][A-E])", text, re.I)
            if rcd_matches:
                rcd = max(rcd_matches, key=lambda x: (int(x[0]), x[1]))
                rcd_source = "tabela_rwy"
        result["reference_code"] = rcd

        # Inferir RCD a partir do TORA quando não explícito
        if not rcd:
            tora_matches = re.findall(
                r"<td[^>]*>\s*(\d{2}[LR]?)\s*</td>\s*<td[^>]*>\s*(\d+)",
                text,
            )
            if tora_matches:
                toras = [int(t[1]) for t in tora_matches if t[1].isdigit()]
                if toras:
                    max_tora = max(toras)
                    rcd = _infer_rcd_from_tora(max_tora)
                    result["reference_code"] = rcd
                    rcd_source = "inferido_tora"
                    logger.debug("eAIS %s: RCD inferido por TORA %dm -> %s", icao, max_tora, rcd)
                    if rcd and not result.get("aircraft_size_category"):
                        lt = rcd[-1].upper()
                        result["aircraft_size_category"] = "A/B" if lt in ("A", "B") else "C" if lt == "C" else "D"

        # aircraft_size_category a partir do RCD
        if rcd and len(rcd) >= 2:
            lt = rcd[-1].upper()
            result["aircraft_size_category"] = "A/B" if lt in ("A", "B") else "C" if lt == "C" else "D"

        # Número de pistas
        idx = text.find("TORA")
        n_runways = 1
        if idx > 0:
            chunk = text[idx : idx + 1200]
            rwy_cells = re.findall(r"<td[^>]*>\s*(\d{2}[LR]?)\s*</td>", chunk)
            if rwy_cells:
                n_runways = max(1, len(rwy_cells) // 2)
        result["number_of_runways"] = n_runways

        # Operações internacionais: designação oficial do eAIS (AD INTL / AD DOM)
        # No HTML do eAIS, "AD" e "INTL"/"DOM" podem estar em elementos separados: <span>AD</span> INTL
        has_intl = (
            "AD INTL" in text
            or bool(re.search(r"AD\s*</[^>]+>\s*INTL", text))
        )
        has_dom = (
            "AD DOM" in text
            or bool(re.search(r"AD\s*</[^>]+>\s*DOM", text))
        )
        if has_intl:
            result["has_international_operations"] = True
        elif has_dom:
            result["has_international_operations"] = False
        else:
            result["has_international_operations"] = False

        # Operações de carga: "voos de carga" ou "AUTH voos de carga" indica que o AD opera carga
        result["has_cargo_operations"] = bool(re.search(r"voos de carga|operações de carga", text, re.I))

        # Facilidades de manutenção: "hangar" ou "hangares" indica infraestrutura
        result["has_maintenance_facility"] = bool(re.search(r"\bhangar(es)?\b", text, re.I))

        result["airport_type"] = "commercial"  # default para aeródromos no eAIS

        # Peso máximo de aeronaves (toneladas) - PRAI "Peso 575.000 Kg" ou "80 toneladas"
        # Prioridade: seção PRAI > busca em toda a página
        def _parse_weight(num_str: str, unit: str) -> Optional[int]:
            s = num_str.replace(" ", "").strip()
            # Formato BR: "575.000" = 575 mil kg; formato US: "575,000" = 575 mil
            if "," in s and len(s.split(",")[-1]) == 3 and s.split(",")[-1].isdigit():
                s = s.replace(",", "").replace(".", "")
            else:
                s = s.replace(".", "").replace(",", ".")
            try:
                val = float(s) if s else 0
                if val <= 0:
                    return None
                u = (unit or "").lower()
                if "tonelada" in u or "ton" in u or u == "t":
                    return int(val)
                if "kg" in u or "quilograma" in u:
                    return int(val / 1000)
                # Sem unidade: se > 1000 provavelmente kg, senão toneladas
                if val > 1000:
                    return int(val / 1000)
                return int(val) if val <= 600 else None
            except (ValueError, ZeroDivisionError):
                return None

        # Seção PRAI/Remoção: ampliar busca para formatos variados do eAIS
        prai_section = ""
        for kw in ["PRAI", "Plano de Remoção", "Remoção de ACFT", "Capacidade para remoção", "SALVAMENTO", "COMBATE"]:
            idx = text.find(kw)
            if idx >= 0:
                prai_section = text[idx : idx + 3500]
                break
        search_text = prai_section if prai_section else text
        # Padrões em ordem de especificidade (mais específico primeiro)
        for pat, unit in [
            (r"ACFT\s+[A-Z0-9\-]+\s*-\s*Peso\s*([\d.,]+)\s*Kg", 0),  # "ACFT A380-800 - Peso 575.000 Kg"
            (r"Capacidade\s+para\s+remoção[^.]*?Peso\s*([\d.,]+)\s*Kg", 0),
            (r"Peso\s+([\d.,\s]+)\s*(Kg|toneladas?|ton\.?|t\b)", 1),
            (r"([\d.,]+)\s*(?:Kg|kg)\b", 0),
            (r"([\d.,]+)\s*toneladas?\b", 0),
            (r"([\d.,]+)\s*ton\.?\b", 0),
            (r"Peso\s+([\d.,]+)\s*(?:Kg)?", 0),
            (r"(?:peso|Peso)\s*m[áa]x[.\s]*[:\-]?\s*([\d.,]+)", 0),
            (r"remoção[^.]*?([\d.,]+)\s*(?:kg|Kg|toneladas?)", 0),
        ]:
            m = re.search(pat, search_text, re.I)
            if m:
                u = m.group(2) if unit == 1 and m.lastindex >= 2 else ""
                w = _parse_weight(m.group(1), u)
                if w and 1 <= w <= 600:  # faixa plausível (1t a A380 ~575t)
                    # Evitar falso positivo: PRAI pode citar aeronave mínima (ex: Learjet 6.300 kg)
                    # Aeroportos 4C/4D/4E operam jatos >30t; peso <30t é suspeito
                    rcd_val = result.get("reference_code") or rcd
                    if rcd_val and rcd_val[-1] in ("C", "D", "E") and w < 30:
                        logger.debug("eAIS %s: peso %dt ignorado (RCD %s sugere aeronaves maiores)", icao, w, rcd_val)
                        continue
                    result["max_aircraft_weight"] = w
                    break

        # Fallback: inferir max_aircraft_weight do RCD quando PRAI não tem peso explícito
        if not result.get("max_aircraft_weight") and rcd and len(rcd) >= 2:
            num, letter = int(rcd[0]) if rcd[0].isdigit() else 1, rcd[-1].upper()
            if num >= 4 and letter in ("D", "E"):
                result["max_aircraft_weight"] = 400 if letter == "D" else 575
            elif num >= 4:
                result["max_aircraft_weight"] = 80
            elif num >= 3:
                result["max_aircraft_weight"] = 80 if letter in ("C", "D", "E") else 50
            else:
                result["max_aircraft_weight"] = 50

        # Fallback: inferir usage/avsec do RCD quando CAT CIVIL não encontrada
        if not result.get("usage_class") and rcd:
            num = int(rcd[0]) if rcd[0].isdigit() else 1
            letter = rcd[-1].upper() if len(rcd) > 1 else "C"
            if num >= 4 and letter in ("D", "E"):
                result["usage_class"], result["avsec_classification"] = "IV", "AP-3"
            elif num >= 4:
                result["usage_class"], result["avsec_classification"] = "III", "AP-2"
            elif num >= 3:
                result["usage_class"], result["avsec_classification"] = "II", "AP-1"
            else:
                result["usage_class"], result["avsec_classification"] = "I", "AP-1"

        # Log campos ausentes em nível DEBUG (útil para diagnóstico)
        missing = [k for k in ("city", "state", "latitude", "longitude", "reference_code", "fire_category", "max_aircraft_weight") if result.get(k) is None]
        if missing:
            logger.debug("eAIS %s: campos não extraídos: %s", icao, missing)

        return result
    except requests.RequestException as e:
        logger.warning("eAIS: erro de requisição para %s: %s", icao_code, e)
        return None
    except Exception as e:
        logger.exception("eAIS: erro inesperado ao extrair %s: %s", icao_code, e)
        return None


def fetch_eais_raw_html(icao_code: str) -> Optional[str]:
    """
    Busca o HTML bruto do eAIS para um aeródromo.
    Usado pelo endpoint de diagnóstico.
    """
    icao = icao_code.upper().strip()
    if len(icao) != 4 or not icao.isalpha():
        return None
    try:
        r = requests.get(EAIS_URL.format(icao=icao), headers=HEADERS, timeout=20)
        r.raise_for_status()
        return r.text
    except Exception as e:
        logger.warning("eAIS raw: erro ao buscar HTML para %s: %s", icao_code, e)
        return None
