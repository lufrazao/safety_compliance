"""
Testes para extração de dados do eAIS (eais_fetch).
Usa HTML mockado para testes unitários; teste de integração opcional com eAIS real.
"""
import pytest
from unittest.mock import patch, MagicMock

# HTML mockado baseado na estrutura real do eAIS (SBGR)
HTML_SBGR = """
<!DOCTYPE html>
<html>
<head><title>AISWEB</title></head>
<body>
<h1>Guarulhos - Governador André Franco Montoro (SBGR) <span>São Paulo/SP  &nbsp;</span></h1>
<span title="Estado">SP</span>
<p>23 26 08S/046 28 23W</p>
<p>CAT CIVIL - 10</p>
<p>compatíveis com o RCD 4E</p>
<p>PRAI: Peso 575.000 Kg</p>
<span title="Aeródromo">AD</span> INTL
<p>AUTH voos de carga e voos não regulares</p>
<table><tr><td>TORA</td></tr>
<tr><td>10L</td><td>3700</td></tr>
<tr><td>28R</td><td>3700</td></tr>
<tr><td>10R</td><td>3000</td></tr>
<tr><td>28L</td><td>3000</td></tr>
</table>
</body>
</html>
"""

# HTML com AD DOM (doméstico) e RCD inferido por TORA
HTML_DOM = """
<h1>Aeródromo Teste (SBTX) <span>Campo Grande/MS</span></h1>
<span title="Estado">MS</span>
<p>20 28 00S/054 40 00W</p>
<p>CAT CIVIL - 5</p>
<span title="Aeródromo">AD</span> DOM
<table><tr><td>TORA</td></tr>
<tr><td>18</td><td>1500</td></tr>
</table>
"""

# HTML com formato AD/INTL em elementos separados (como no eAIS real)
HTML_AD_SPAN_INTL = """
<h1>Campinas (SBCG) <span>Campinas/SP</span></h1>
<span title="Estado">SP</span>
<p>23 00 00S/047 08 00W</p>
<p>CAT CIVIL - 7</p>
<span title="Aeródromo">AD</span>
INTL
<p>via de acesso aos hangares CIV</p>
<p>PRAI: 80 toneladas</p>
<table><tr><td>TORA</td></tr>
<tr><td>02</td><td>3200</td></tr>
</table>
"""

# HTML inválido - sem código nem Aeródromo
HTML_INVALID = """
<!DOCTYPE html>
<html><body>
<h1>Página não encontrada</h1>
<p>O aeródromo solicitado não existe.</p>
</body></html>
"""


@pytest.fixture
def mock_requests():
    """Mock de requests.get para evitar chamadas reais ao eAIS."""
    with patch("app.services.eais_fetch.requests.get") as mock_get:
        yield mock_get


def test_fetch_sbgr_mock(mock_requests):
    """Extrai corretamente dados do SBGR com HTML mockado."""
    mock_resp = MagicMock()
    mock_resp.text = HTML_SBGR
    mock_resp.raise_for_status = MagicMock()
    mock_requests.return_value = mock_resp

    from app.services.eais_fetch import fetch_eais_airport

    result = fetch_eais_airport("SBGR")
    assert result is not None
    assert result["name"] == "Guarulhos - Governador André Franco Montoro"
    assert result["code"] == "SBGR"
    assert result["city"] == "São Paulo"
    assert result["state"] == "SP"
    assert result["reference_code"] == "4E"
    assert result["fire_category"] == 10
    assert result["usage_class"] == "IV"
    assert result["avsec_classification"] == "AP-3"
    assert result["max_aircraft_weight"] == 575
    assert result["has_international_operations"] is True
    assert result["has_cargo_operations"] is True
    assert result["number_of_runways"] >= 1
    assert -90 <= result["latitude"] <= 90
    assert -180 <= result["longitude"] <= 180


def test_fetch_ad_dom(mock_requests):
    """Extrai AD DOM (operações domésticas)."""
    mock_resp = MagicMock()
    mock_resp.text = HTML_DOM
    mock_resp.raise_for_status = MagicMock()
    mock_requests.return_value = mock_resp

    from app.services.eais_fetch import fetch_eais_airport

    result = fetch_eais_airport("SBTX")
    assert result is not None
    assert result["has_international_operations"] is False
    assert result["reference_code"] == "4C"  # inferido por TORA 1500m


def test_fetch_ad_span_intl(mock_requests):
    """Reconhece AD INTL quando AD e INTL estão em elementos separados."""
    mock_resp = MagicMock()
    mock_resp.text = HTML_AD_SPAN_INTL
    mock_resp.raise_for_status = MagicMock()
    mock_requests.return_value = mock_resp

    from app.services.eais_fetch import fetch_eais_airport

    result = fetch_eais_airport("SBCG")
    assert result is not None
    assert result["has_international_operations"] is True
    assert result["has_maintenance_facility"] is True
    assert result["max_aircraft_weight"] == 80


def test_fetch_invalid_page(mock_requests):
    """Retorna None quando página não contém aeródromo válido."""
    mock_resp = MagicMock()
    mock_resp.text = HTML_INVALID
    mock_resp.raise_for_status = MagicMock()
    mock_requests.return_value = mock_resp

    from app.services.eais_fetch import fetch_eais_airport

    result = fetch_eais_airport("XXXX")
    assert result is None


def test_fetch_invalid_icao():
    """Retorna None para código ICAO inválido."""
    from app.services.eais_fetch import fetch_eais_airport

    assert fetch_eais_airport("") is None
    assert fetch_eais_airport("ABC") is None  # 3 letras
    assert fetch_eais_airport("1234") is None  # números
    assert fetch_eais_airport("SDU") is None  # 3 letras (IATA)


def test_infer_rcd_from_tora():
    """Inferência de RCD a partir do TORA."""
    from app.services.eais_fetch import _infer_rcd_from_tora

    assert _infer_rcd_from_tora(3700) == "4E"
    assert _infer_rcd_from_tora(2500) == "4C"
    assert _infer_rcd_from_tora(1500) == "4C"
    assert _infer_rcd_from_tora(1000) == "3C"
    assert _infer_rcd_from_tora(850) == "3B"
    assert _infer_rcd_from_tora(500) is None


def test_infer_usage_avsec():
    """Inferência de usage_class e avsec a partir da CAT CIVIL."""
    from app.services.eais_fetch import _infer_usage_avsec_from_cat

    assert _infer_usage_avsec_from_cat(10) == ("IV", "AP-3")
    assert _infer_usage_avsec_from_cat(7) == ("IV", "AP-3")
    assert _infer_usage_avsec_from_cat(5) == ("III", "AP-2")
    assert _infer_usage_avsec_from_cat(3) == ("II", "AP-1")
    assert _infer_usage_avsec_from_cat(1) == ("I", "AP-1")


@pytest.mark.skip(reason="Requer acesso ao eAIS; use EAIS_INTEGRATION=1 para rodar")
def test_fetch_sbgr_integration():
    """Teste de integração com eAIS real (opcional)."""
    import os
    if os.getenv("EAIS_INTEGRATION") != "1":
        pytest.skip("Defina EAIS_INTEGRATION=1 para rodar teste de integração")

    from app.services.eais_fetch import fetch_eais_airport

    result = fetch_eais_airport("SBGR")
    assert result is not None
    assert result["name"]
    assert result["reference_code"] in ("4C", "4E")
    assert result["fire_category"] >= 1
