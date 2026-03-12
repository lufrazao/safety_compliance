# Claude Documentation

Documentação do sistema de conformidade aeroportuária ANAC para orientar desenvolvimento e manutenção.

## Visão Geral

Sistema de gestão de conformidade para aeroportos brasileiros, desenvolvido para apoiar coordenadores SESCINC na gestão de procedimentos e certificação de conformidade com os requisitos da ANAC (RBAC-153 e RBAC-154). As informações são importadas da ANAC e o sistema faz a inferência correta de quais normas se aplicam a cada aeroporto.

## Estrutura do Projeto

```
safety_compliance/
├── app/
│   ├── main.py              # FastAPI, endpoints, serialização
│   ├── models.py            # SQLAlchemy (Airport, Regulation, ComplianceRecord)
│   ├── schemas.py           # Pydantic
│   ├── database.py          # SQLite
│   ├── compliance_engine.py # Motor de verificação (regulation_applies_to_airport)
│   ├── seed_data.py         # Normas RBAC-153/154 (seed incremental)
│   └── services/
│       ├── anac_sync.py      # Sincronização com ANAC
│       └── eais_fetch.py     # Busca eAIS (RCD, CAT CIVIL)
├── static/
│   └── index.html           # Frontend SPA (abas: Aeroportos, Conformidade, Áreas, Prazos)
├── RBAC/                    # Documentos de referência
│   ├── CEF RBAC 153.pdf
│   ├── 01 Apostila - CURSO BÁSICO DE GESTÃO DO SESCINC...
│   └── RBAC_REFERENCIAS_SME_COE_PCM.md
├── migrations/              # Scripts de migração
└── data/                    # Cache ANAC (anac_airports_cache.json)
```

## Áreas REA (Resposta a Emergência Aeroportuária)

O sistema organiza a conformidade em 6 áreas conforme documento Sistema.xlsx:

| Área | Códigos RBAC | Descrição |
|------|--------------|-----------|
| **SESCINC** | RBAC-153-01 a 14 (exceto 11) | Serviço de Salvamento e Combate a Incêndio |
| **SME** | RBAC-153-15 | Serviço Médico de Emergência (ambulâncias) |
| **COE** | RBAC-153-16 | Centro de Operações de Emergências |
| **PCM** | RBAC-153-17 | Posto de Comando Móvel |
| **SIMULADOS** | RBAC-154-43 | Exercícios Simulados de Emergência (ESEA) |
| **PLANOS** | RBAC-153-11, RBAC-154-40 | PLEM, PCINC e planos relacionados |

O mapeamento `getFunctionalArea(code)` está em `static/index.html` em várias funções (displayAreasFunctional, filterByArea, exportAreaReport, generateAreaReport, displayDeadlines, displayCompliance).

## Mapeamento de Normas e Aplicabilidade

### Inferência a partir dos dados ANAC

O `compliance_engine.regulation_applies_to_airport()` usa:

- **usage_class** (I, II, III, IV, PRIVADO) → infere `size` e `annual_passengers`
- **applies_to_sizes** → small, medium, large, international
- **applies_to_types** → commercial, mixed, general_aviation
- **min_passengers** → compara com `annual_passengers` (inferido de usage_class)

### Aplicabilidade por Classe

| Classe | usage_class | annual_passengers | SME, COE, PCM |
|--------|-------------|-------------------|---------------|
| I | I | 100k | Não |
| II | II | 600k | Sim |
| III | III | 3M | Sim |
| IV | IV | 10M | Sim |
| Privado | PRIVADO | 0 | Não |

### Códigos de Normas no Seed

- **RBAC-153-01 a 14**: SESCINC (CCI, equipe, tempo-resposta, PCINC, etc.)
- **RBAC-153-15**: SME (153.309 – ambulâncias)
- **RBAC-153-16**: COE (153.301)
- **RBAC-153-17**: PCM (153.313)
- **RBAC-154-40**: PLEM
- **RBAC-154-43**: Exercícios simulados

## Classificações ANAC

### Por Uso (RBAC 153)
- Classe I: < 200 mil passageiros/ano
- Classe II: 200 mil - 1 milhão
- Classe III: 1 milhão - 5 milhões
- Classe IV: > 5 milhões
- Privado: Uso restrito ao proprietário

### AVSEC
- AP-0, AP-1, AP-2, AP-3

### Categoria de Porte da Aeronave
- A/B, C, D

## Fluxos Principais

1. **Cadastro de aeroporto**: Busca ANAC por código ICAO → preenche usage_class, avsec, reference_code → calcula size e annual_passengers.
2. **Verificar Conformidade**: `POST /api/compliance/check` → `regulation_applies_to_airport` para cada norma → cria/atualiza `compliance_records`.
3. **Atualizar todas**: `POST /api/compliance/refresh-all` → executa check para todos os aeroportos (útil após adicionar novas normas).
4. **Aba Áreas**: Carrega compliance_records, agrupa por `getFunctionalArea(code)`, exibe cards SESCINC, SME, COE, PCM, SIMULADOS, PLANOS.

## Tecnologias

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Banco**: SQLite
- **Validação**: Pydantic

## Fontes de Dados

- **ANAC**: Lista de aeródromos, lookup por ICAO (`/api/airports/lookup/{code}`)
- **eAIS**: RCD, CAT CIVIL, pistas (busca manual)
- **RBAC/**: CEF RBAC 153, Apostila SESCINC (referência local)

## Notas de Desenvolvimento

- Enums Python são convertidos para string antes da serialização JSON
- `usage_class` é string no banco; `size` e `annual_passengers` são calculados automaticamente
- Seed incremental: `seed_regulations()` adiciona apenas normas novas (por código)
- Campos customizados por norma em `compliance_records.custom_fields`
- `fire_category` (CAT CIVIL) existe no modelo mas não é usado no filtro de normas
