# Plano de Ação: Identificação e Melhoria das Falhas na Extração eAIS

Este documento descreve o plano para identificar e corrigir possíveis falhas na extração de dados do eAIS para o cadastro de aeroportos.

---

## Fase 1: Diagnóstico e Observabilidade

### 1.1 Adicionar logging de erros no `eais_fetch.py` ✅

**Objetivo:** Identificar quando e por que a extração falha.

**Ações:**
- [x] Capturar e registrar exceções em `fetch_eais_airport()` (em vez de retornar `None` silenciosamente)
- [x] Registrar quando `icao not in text and "Aeródromo" not in text` (página inválida ou formato inesperado)
- [x] Opcional: log de quais campos foram extraídos com sucesso vs. ausentes por aeroporto (nível DEBUG)

**Arquivo:** `app/services/eais_fetch.py`

---

### 1.2 Criar endpoint de diagnóstico (opcional) ✅

**Objetivo:** Permitir teste manual da extração para um código ICAO.

**Ações:**
- [x] Endpoint `GET /api/airports/lookup/{icao}/debug` que retorna:
  - Dados extraídos (`extracted`)
  - Campos que falharam (`missing_fields`)
  - Trecho do HTML (`raw_html_preview`, primeiros 3000 caracteres)
  - Tamanho total do HTML (`raw_html_length`)
- [x] Útil para suporte e investigação de aeroportos específicos

**Arquivo:** `app/main.py`

---

## Fase 2: Robustez dos Parsers ✅

### 2.1 Revisar regex de cidade e estado ✅

**Problema:** O padrão `Cidade/UF` pode não cobrir variações do eAIS.

**Ações:**
- [x] Regex principal ampliado: `Cidade/UF` com `[\s<]` além de `&nbsp;` e `</span>`
- [x] Fallbacks: "Cidade - UF" e "Cidade, UF" para tabelas e formatos alternativos
- [x] Testado com SBGR, SBCF, SBCG, SBSP, SBRJ

**Arquivo:** `app/services/eais_fetch.py`

---

### 2.2 Revisar extração de coordenadas ✅

**Problema:** Formato fixo DD MM SS; eAIS pode exibir coordenadas em formato decimal em alguns contextos.

**Ações:**
- [x] Formato principal DD MM SS mantido (padrão do eAIS)
- [x] Fallback: formato graus-minutos-segundos "23°26'08"S" com regex alternativo
- [x] Tratamento de N/S e E/W validado

**Arquivo:** `app/services/eais_fetch.py`

---

### 2.3 Revisar extração de RCD (reference_code) ✅

**Problema:** RCD pode vir de "compatíveis com o RCD X", "RWY XX YY", ou inferência por TORA.

**Ações:**
- [x] Padrões ampliados: "código X", "X (RCD|referência)"
- [x] Prioridade documentada no código: texto > tabela RWY > inferência TORA
- [x] Log em nível DEBUG quando RCD inferido por TORA

**Arquivo:** `app/services/eais_fetch.py`

---

### 2.4 Revisar extração de max_aircraft_weight (PRAI) ✅

**Problema:** Só extraia "Peso X Kg" ou "Peso X toneladas" na seção PRAI.

**Ações:**
- [x] Busca ampliada: seção PRAI primeiro, depois página inteira se vazio
- [x] Formatos: "Peso X Kg", "X toneladas", "X Ton", "Peso X" (inferência por magnitude)
- [x] Faixa de validação 1–600 toneladas para evitar falsos positivos

**Arquivo:** `app/services/eais_fetch.py`

---

## Fase 3: Frontend ✅

### 3.1 Corrigir condições de preenchimento ✅

**Problema:** Uso de `if (data.field)` pode ignorar `0` ou `false` (valores válidos).

**Ações:**
- [x] Todos os campos: usar `if (data.field != null)` para aceitar 0, false e string vazia
- [x] Campos texto: `value = data.field || ''` para normalizar null/undefined
- [x] Checkboxes: `!= null` mantido (correto para true/false)

**Arquivo:** `static/index.html` — função `lookupAirportFromANAC()`

---

### 3.2 Evitar sobrescrita indesejada por calculateANACClassifications ✅

**Problema:** `calculateANACClassifications()` era chamada após o preenchimento e podia sobrescrever valores do eAIS.

**Ações:**
- [x] Quando `data.source === 'eais'`, não chamar `calculateANACClassifications()` — dados já vêm completos
- [x] Quando fonte é local/ANAC, manter recálculo para consistência

**Arquivo:** `static/index.html`

---

## Fase 4: Testes e Validação ✅

### 4.1 Suite de testes de extração ✅

**Objetivo:** Detectar regressões quando o eAIS ou o código mudar.

**Ações:**
- [x] Criado `tests/test_eais_fetch.py` com HTML mockado (SBGR, AD DOM, AD span INTL)
- [x] Testes: fetch SBGR, AD DOM, AD span INTL, página inválida, ICAO inválido
- [x] Testes de funções auxiliares: _infer_rcd_from_tora, _infer_usage_avsec_from_cat
- [x] Teste de integração opcional com `@pytest.mark.skip` e `EAIS_INTEGRATION=1`

**Arquivo:** `tests/test_eais_fetch.py`

---

### 4.2 Teste de integração frontend

**Objetivo:** Garantir que o formulário seja preenchido corretamente com a resposta da API.

**Ações:**
- [ ] Simular resposta da API e verificar que todos os campos são preenchidos
- [ ] Testar cenários: todos os campos preenchidos, campos parciais, valores `0` e `false`
- [ ] Verificar que checkboxes refletem corretamente `true`/`false`

**Arquivo:** `tests/` ou teste manual documentado (ver `docs/EAIS_FORMATS.md`)

---

## Fase 5: Documentação e Manutenção ✅

### 5.1 Documentar formatos do eAIS ✅

**Ações:**
- [x] Criado `docs/EAIS_FORMATS.md` com estrutura HTML, padrões por campo e aeroportos de referência
- [x] Incluído link para o eAIS e data da última verificação

---

### 5.2 Processo de revisão periódica ✅

**Ações:**
- [x] Documentado em `docs/EAIS_FORMATS.md`: periodicidade trimestral, checklist e comando de teste

---

## Priorização Sugerida

| Prioridade | Item                          | Impacto | Esforço |
|-----------|-------------------------------|---------|---------|
| Alta      | 1.1 Logging de erros          | Alto    | Baixo   |
| Alta      | 3.1 Condições de preenchimento| Alto    | Baixo   |
| Média     | 2.1–2.4 Robustez dos parsers | Alto    | Médio   |
| Média     | 4.1 Suite de testes           | Médio   | Médio   |
| Baixa     | 1.2 Endpoint de diagnóstico   | Baixo   | Baixo   |
| Baixa     | 5.1–5.2 Documentação          | Médio   | Baixo   |

---

## Cronograma Sugerido

- **Sprint 1:** Fase 1 (logging) + Fase 3.1 (frontend)
- **Sprint 2:** Fase 2 (parsers) — itens 2.1 a 2.4
- **Sprint 3:** Fase 4 (testes) + Fase 5 (documentação)
- **Contínuo:** Fase 5.2 (revisão periódica)

---

## Critérios de Conclusão

- [x] Logging implementado e exceções registradas
- [x] Frontend preenche corretamente todos os campos, incluindo `0` e `false`
- [x] Parsers revisados e fallbacks adicionados onde aplicável
- [x] Testes automatizados para extração (7 testes em `tests/test_eais_fetch.py`)
- [x] Documentação de formatos do eAIS criada (`docs/EAIS_FORMATS.md`) e revisão periódica definida
