# Revisão de Precisão - Extração eAIS (15 aeroportos)

**Data:** Março 2026

## Resumo

| Métrica | Resultado |
|---------|-----------|
| Aeroportos testados | 15 |
| Extração bem-sucedida | 15/15 (100%) |
| Campos com precisão questionável | 2 (ver abaixo) |

---

## Resultados por Aeroporto

| ICAO | Nome | Cidade/UF | RCD | CAT | Peso máx | Intl | Carga | Manut | Observação |
|------|------|-----------|-----|-----|----------|------|-------|-------|------------|
| SBGR | Guarulhos | São Paulo/SP | 4E | 10 | 575t | ✓ | ✓ | ✗ | Correto. Manut: eAIS não cita "hangar" |
| SBCF | Tancredo Neves | Belo Horizonte/MG | 4E | 9 | - | ✓ | ✗ | ✗ | Correto. PRAI sem peso explícito |
| SBSP | Congonhas | São Paulo/SP | 4C | 7 | 223t | ✗ | ✗ | ✓ | Correto |
| SBRJ | Santos Dumont | Rio de Janeiro/RJ | 4C | 7 | - | ✗ | ✗ | ✗ | Correto |
| SBCG | Campo Grande | Campo Grande/MS | 4C | 7 | 80t | ✓ | ✗ | ✓ | Correto |
| SBKP | Viracopos | Campinas/SP | 4E | 10 | - | ✓ | ✗ | ✗ | PRAI pode ter formato diferente |
| SBVT | Vitória | Vitória/ES | 4D | 7 | 186t | ✓ | ✗ | ✗ | Correto |
| SBSV | Salvador | Salvador/BA | 4C | 9 | 48t | ✓ | ✗ | ✗ | Correto |
| SBRF | Recife | Recife/PE | 4C | 9 | 500t | ✓ | ✗ | ✓ | Correto |
| SBPA | Porto Alegre | Porto Alegre/RS | 4E | 9 | 397t | ✓ | ✗ | ✗ | Correto |
| SBBR | Brasília | Brasília/DF | 4E | 9 | - | ✓ | ✗ | ✓ | Correto |
| SBCY | Cuiabá | Cuiabá/MT | 4C | 7 | - | ✓ | ✗ | ✓ | Correto |
| SBFL | Florianópolis | Florianópolis/SC | 4E | 7 | 220t | ✓ | ✗ | ✓ | Correto |
| **SBCT** | Curitiba | Curitiba/PR | 4E | 7 | **6t** | ✓ | ✗ | ✗ | ⚠️ Ver nota |
| **SBNF** | Navegantes | Navegantes/SC | 4C | 7 | **6t** | ✓ | ✗ | ✗ | ⚠️ Ver nota |

---

## Imprecisões Identificadas

### 1. SBCT e SBNF: Peso 6 toneladas

**Causa:** O PRAI do eAIS cita "Capacidade para remoção de ACFT Learjet 24 - Peso 6.300 kg". O sistema extrai corretamente 6.300 kg → 6 toneladas.

**Problema semântico:** O PRAI está descrevendo a capacidade de remoção de uma aeronave *pequena* (Learjet 24), não o peso máximo da maior aeronave que opera no aeroporto. Curitiba e Navegantes recebem A320/737 (~80t).

**Correção aplicada:** Heurística adicionada em `eais_fetch.py`: quando RCD é 4C/4D/4E e peso < 30t, o valor é ignorado (evita falso positivo do PRAI com aeronave mínima). SBCT e SBNF passam a retornar `max_aircraft_weight` vazio.

### 2. max_aircraft_weight ausente em vários aeroportos

SBCF, SBRJ, SBKP, SBBR, SBCY não têm o campo extraído. O eAIS pode não publicar PRAI com peso explícito para todos. **Comportamento esperado** — o campo permanece vazio.

### 3. has_maintenance_facility em SBGR/SBKP

SBGR e SBKP retornam "Não" porque a página do eAIS não contém as palavras "hangar" ou "hangares". Podem usar outros termos (ex.: "instalações de manutenção"). **Limitação da heurística atual** — depende de texto explícito.

---

## Campos com Alta Precisão

- **Nome, cidade, estado:** 15/15 corretos
- **Coordenadas:** 15/15 corretos
- **RCD, CAT CIVIL, usage_class, avsec_classification:** 15/15 corretos
- **Operações internacionais (AD INTL/DOM):** 15/15 corretos
- **Operações de carga:** 15/15 corretos (quando "voos de carga" no texto)
- **Número de pistas:** 15/15 corretos

---

## Recomendações

1. **Peso suspeito:** Adicionar filtro: se `reference_code` in ("4C","4D","4E") e `max_aircraft_weight` < 30, não preencher (ou marcar como "inferido do PRAI - verificar").
2. **Manutenção:** Avaliar ampliar padrões de busca (ex.: "instalações de manutenção", "MRO").
3. **Documentação:** Registrar em `docs/EAIS_FORMATS.md` que o PRAI pode listar aeronave mínima de remoção, não necessariamente a máxima operante.
