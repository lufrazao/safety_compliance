# Análise: Dados eAIS vs. Requisitos das Áreas (v1)

## Áreas contempladas na primeira versão

1. **SESCINC** – Serviço de Salvamento e Combate a Incêndio  
2. **SME** – Serviço Médico de Emergência e Remoção de Vítimas  
3. **COE** – Centro de Operações de Emergências  
4. **PCM** – Posto de Coordenação Móvel  

---

## Dados atualmente extraídos do eAIS

| Campo | Uso | Fonte no eAIS |
|-------|-----|---------------|
| `name` | Identificação | h1 |
| `code` | ICAO | URL/contexto |
| `city`, `state` | Localização | Cidade/UF |
| `latitude`, `longitude` | Coordenadas | COMPL |
| `fire_category` (CAT CIVIL 1–10) | SESCINC | COMPL / RFFS |
| `reference_code` (RCD) | SESCINC, operações | INFORMAÇÃO ADICIONAL / ROTAER |
| `aircraft_size_category` | SESCINC, compatibilidade | Inferido do RCD |
| `number_of_runways` | SESCINC (MGI, tempo-resposta) | Tabela TORA |
| `usage_class`, `avsec_classification` | Aplicabilidade | Inferido da CAT/RCD |
| `has_international_operations` | Aplicabilidade | AD INTL / AD DOM |
| `airport_type` | Tipo | Default commercial |

---

## Mapeamento por área

### 1. SESCINC – Serviço de Salvamento e Combate a Incêndio

**Tarefas principais (RBAC-153):**
- Determinação da CAT (RBAC-153-01)
- Operações compatíveis com a CAT (RBAC-153-02)
- CCI, veículos de apoio, agentes extintores (RBAC-153-03, 04, 05)
- Equipe, tempo-resposta, capacitação (RBAC-153-06, 07, 08)
- PCINC (RBAC-153-11)

**Dados necessários do eAIS:**

| Requisito | Dado eAIS | Status |
|-----------|-----------|--------|
| CAT do aeródromo | `fire_category` (CAT CIVIL) | ✅ Extraído |
| Maior aeronave / RCD | `reference_code`, `aircraft_size_category` | ✅ Extraído |
| Número de pistas (MGI, tempo-resposta) | `number_of_runways` | ✅ Extraído |
| Aplicabilidade (classe, AVSEC) | `usage_class`, `avsec_classification` | ✅ Inferido |

**Conclusão SESCINC:** Dados do eAIS cobrem bem os requisitos desta área.

---

### 2. SME – Serviço Médico de Emergência e Remoção de Vítimas

**Tarefas principais:**
- Coordenação médica em emergências
- Remoção de vítimas
- Integração com PLEM/PCINC

**Dados no eAIS:**
- Seção MET CIVIL com CMA (Centro de Medicina Aeroespacial) e telefones
- Não há seção específica “SME” no eAIS

**Status:** O eAIS não publica dados estruturados de SME. A área é tratada por procedimentos (PLEM/PCINC) e não por dados fixos do AIP. Não há extração adicional necessária do eAIS para SME.

---

### 3. COE – Centro de Operações de Emergências

**Tarefas principais (checklist ANAC):**
- Capacidade máxima de remoção (modelo e peso da maior aeronave)
- Contatos para coordenação do PRAI
- Acionamento de recursos (PRAI, PLEM)
- Identificação da capacidade de remoção (prevista no AIS – AIP AD2 e PLEM)

**Dados no eAIS (seção “SERVIÇOS DE SALVAMENTO E COMBATE A INCÊNDIO”):**

Exemplo SBGR:
> Plano de Remoção de ACFT inoperantes (PRAI): Capacidade para remoção até **ACFT A380-800 - Peso 575.000 Kg**, sob responsabilidade do proprietário ou explorador, em coordenação com a administração aeroportuária, **TEL: Centro de Operações de Emergência - COE (11) 2445-2200** e Recovery Team (11) 95469-0889...

**Dados necessários do eAIS:**

| Requisito | Dado eAIS | Status |
|-----------|-----------|--------|
**Conclusão COE:** Seção COE removida do cadastro — dados avaliados em procedimentos/TOPS, não no cadastro.

---

### 4. PCM – Posto de Coordenação Móvel

**Tarefas principais (checklist ANAC):**
- Responsável preferencial: supervisor de pátio
- Acionamento pelo COE para deslocamento
- Avaliação em testes operacionais (TOPS)

**Dados no eAIS:**
- O eAIS não publica dados específicos de PCM (responsável, posicionamento, etc.).

**Status:** PCM é avaliado em testes operacionais e procedimentos, não em dados fixos do AIP. Não há extração adicional necessária do eAIS para PCM.

---

## Resumo e recomendações

### Dados suficientes (sem alteração)
- **SESCINC:** CAT CIVIL, RCD, `aircraft_size_category`, `number_of_runways`, classificações
- **SME:** Não depende de dados estruturados do eAIS
- **PCM:** Não depende de dados estruturados do eAIS

### Dados faltando (COE)

Para apoiar as tarefas do COE, sugere-se extrair da seção “SERVIÇOS DE SALVAMENTO E COMBATE A INCÊNDIO”:

| Campo sugerido | Descrição | Exemplo |
|----------------|-----------|---------|
| `prai_capacity_model` | Modelo da maior aeronave que o aeródromo pode remover | "A380-800" |
| `prai_capacity_weight_kg` | Peso em kg da maior aeronave | 575000 |

### Padrões de extração sugeridos

1. **Capacidade PRAI:**  
   `Capacidade para remoção até ACFT ([A-Z0-9\-]+)\s*-\s*Peso\s*([\d.]+)\s*Kg`

2. **Telefone COE:**  
   `COE\s*\(([^)]+)\)` ou `Centro de Operações de Emergência[^.]*?\((\d[\d\s\-]+)\)`

3. **Recovery Kit:**  
   `AD dispõe de Recovery Kit` ou `Recovery Kit`

---

## Implementação (concluída)

1. ~~Seção COE removida~~ — Telefone COE e Recovery Kit não fazem parte do cadastro de aeroportos
