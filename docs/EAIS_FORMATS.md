# Formatos do eAIS (AISWEB) para Extração de Dados

**Fonte:** [AISWEB - Informações Aeronáuticas do Brasil](https://aisweb.decea.mil.br/?codigo=XXXX&i=aerodromos)  
**Última verificação:** Março 2026

Este documento descreve a estrutura do HTML e os padrões de texto usados pelo sistema para extrair dados de aeródromos do eAIS.

---

## URL e Estrutura Geral

- **URL:** `https://aisweb.decea.mil.br/?codigo={ICAO}&i=aerodromos`
- **Exemplo:** `https://aisweb.decea.mil.br/?codigo=SBGR&i=aerodromos`
- O conteúdo é retornado via HTTP GET (sem JavaScript obrigatório para dados principais)

---

## Campos Extraídos e Padrões

### 1. Nome do Aeródromo

**Fonte:** Tag `<h1>`

**Padrão:** `Nome do Aeródromo (ICAO)` — ex.: `Guarulhos - Governador André Franco Montoro (SBGR)`

**Regex:** `(.+?)\s*\(\s*{ICAO}\s*\)` dentro do conteúdo do h1

---

### 2. Cidade e Estado (UF)

**Formatos suportados:**

| Formato | Exemplo | Regex principal |
|---------|---------|-----------------|
| Cidade/UF | São Paulo/SP | `([A-Za-zÀ-ÿ...])/\s*([A-Z]{2})` |
| Cidade - UF | Campo Grande - MS | Fallback |
| Cidade, UF | Belo Horizonte, MG | Fallback |

**Estado alternativo:** `<span title="Estado">SP</span>`

---

### 3. Coordenadas

**Formato principal:** DD MM SS N/S e DDD MM SS E/W  
**Exemplo:** `23 26 08S/046 28 23W`

**Formato alternativo:** Graus-minutos-segundos com símbolos — `23°26'08"S 046°28'23"W`

---

### 4. CAT CIVIL (Categoria Contraincêndio)

**Padrão:** `CAT CIVIL - N` (N de 1 a 10)

**Exemplo:** `CAT CIVIL - 10`

Usado para inferir `usage_class` e `avsec_classification`.

---

### 5. RCD (Reference Code / Código de Referência)

**Prioridade de extração:**

1. **Texto explícito:** "compatíveis com o RCD 4E", "RCD 4E", "código 4C", "4E ou inferior"
2. **Tabela RWY:** "RWY 02L/20R 3C" ou "RWY 10L 4E"
3. **Inferência por TORA:** quando não explícito, inferido do comprimento da pista (metros)

**Tabela de inferência TORA → RCD:**
- ≥ 3000 m → 4E
- ≥ 1800 m → 4C
- ≥ 1200 m → 4C
- ≥ 900 m → 3C
- ≥ 800 m → 3B

---

### 6. Operações Internacionais (AD INTL / AD DOM)

**Problema:** No HTML, "AD" e "INTL"/"DOM" podem estar em elementos separados:
```html
<span title="Aeródromo">AD</span> INTL
```

**Padrões:** `AD INTL`, `AD DOM`, ou regex `AD\s*</[^>]+>\s*INTL`

---

### 7. Operações de Carga

**Padrões:** "voos de carga", "operações de carga", "AUTH voos de carga"

---

### 8. Facilidades de Manutenção

**Padrões:** "hangar", "hangares" (palavra inteira)

---

### 9. Peso Máximo de Aeronaves (PRAI)

**Seção:** PRAI ou "Plano de Remoção"

**Formatos suportados:**
- `Peso 575.000 Kg`
- `Peso 80 toneladas`
- `223 Ton`
- `80 toneladas`

**Faixa válida:** 1 a 600 toneladas (evitar falsos positivos)

---

### 10. Número de Pistas

**Fonte:** Tabela TORA — contagem de células com designação de pista (ex.: 10L, 28R)

**Cálculo:** `len(rwy_cells) // 2`

---

## Aeroportos de Referência para Testes

| ICAO | Nome | Características |
|------|------|-----------------|
| SBGR | Guarulhos | AD INTL, carga, CAT 10, RCD 4E, PRAI 575t |
| SBCF | Confins | AD INTL, CAT 9 |
| SBCG | Campo Grande | AD INTL, hangares, PRAI 80t |
| SBSP | Congonhas | AD DOM, PRAI 223 Ton |
| SBRJ | Santos Dumont | AD DOM, CAT 7 |

---

## Revisão Periódica

**Recomendação:** Revisar trimestralmente se o eAIS alterou a estrutura.

**Checklist:**
1. Rodar extração para SBGR, SBCF, SBCG, SBSP, SBRJ
2. Comparar com valores esperados (ver `tests/test_eais_fetch.py`)
3. Se houver falhas: atualizar parsers em `app/services/eais_fetch.py` e este documento

**Teste rápido:**
```bash
python -m pytest tests/test_eais_fetch.py -v
```
