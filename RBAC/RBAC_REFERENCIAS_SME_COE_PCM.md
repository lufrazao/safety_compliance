# Referências RBAC 153 - SME, COE e PCM

Documento extraído dos arquivos em `/Users/Luciana/safety_compliance/RBAC/`:
- **CEF RBAC 153.pdf** – Compêndio de Elementos de Fiscalização
- **01 Apostila - CURSO BÁSICO DE GESTÃO DO SESCINC 05_03_2024.pdf**

## Estrutura Subparte F (Resposta à Emergência Aeroportuária)

A Subparte F do RBAC 153 trata do SREA (Sistema de Resposta à Emergência Aeroportuária) e inclui:

### SME (Serviço Médico de Emergência) – Ambulâncias

| Artigo RBAC | Descrição | Aplicabilidade |
|-------------|-----------|----------------|
| **153.309 (a)** | Quantidade mínima de ambulâncias tripuladas conforme ANVISA e Ministério da Saúde | Classe II, III, IV |
| **153.309 (a)(1)** | Condutor habilitado e capacitado para ambulâncias | Classe II, III, IV |
| **153.309 (a)(2)** | Tripulação mínima conforme MS e ANVISA | Classe II, III, IV |
| **153.309 (a)(3)** | Características técnicas e operacionais conforme MS e ANVISA | Classe II, III, IV |

**Quantidade mínima por classe:**
- Classe II: mínimo 1 ambulância
- Classe III: mínimo 1 ambulância
- Classe IV: mínimo 2 ambulâncias (sendo uma tipo D)

### PCM (Posto de Comando Móvel)

| Artigo RBAC | Descrição | Aplicabilidade |
|-------------|-----------|----------------|
| **153.313 (a)(b)** | PCM – locomoção e acessibilidade: interno ao aeródromo, fácil acesso, rápida locomoção até o local da emergência | Classe II, III, IV |
| **153.313 (c)** | PCM – comunicação imediata e segura com o COE e recursos envolvidos | Classe II, III, IV |
| **153.313 (d)** | PCM – iluminação para suporte às atividades | Classe II, III, IV |
| **153.313 (e)** | PCM – definição de responsável pela operação no planejamento do SREA | Classe II, III, IV |

### COE (Centro de Operações de Emergências)

O COE é referenciado no RBAC 153 como estrutura com a qual o PCM deve manter comunicação. Conforme a apostila:
- O COE é o centro de operações que coordena a resposta às emergências
- O PCM comunica-se com o COE
- **153.301** – Generalidades do SREA incluem divulgação de informações, procedimentos e responsabilidades
- **153.301 (d)** – Referência ao plano de emergências

O COE é parte do planejamento do SREA (Sistema de Resposta à Emergência Aeroportuária), exigido pelas Subpartes F e G do RBAC 153.

## Mapeamento para o Sistema

Para implementar no seed e mapear para as áreas REA:

| Área | Código sugerido | Referência ANAC | Descrição |
|------|-----------------|-----------------|-----------|
| **SME** | RBAC-153-15 | 153.309 | Ambulâncias – quantidade, tripulação, certificação |
| **COE** | RBAC-153-16 | 153.301, 153.303 | Centro de Operações de Emergências – existência, ativação, composição |
| **PCM** | RBAC-153-17 | 153.313 | Posto de Comando Móvel – locomoção, comunicação, iluminação, responsável |

## Arquivos de Referência

| Arquivo | Localização | Conteúdo |
|---------|-------------|----------|
| CEF RBAC 153 | `RBAC/CEF RBAC 153.pdf` | Elementos de fiscalização com artigos e requisitos |
| Apostila SESCINC | `RBAC/01 Apostila - CURSO BÁSICO DE GESTÃO DO SESCINC 05_03_2024.pdf` | Gestão do SESCINC, SME, COE, PCM, PLEM |
| Perguntas e Respostas RBAC 154 | `RBAC/Perguntas e Respostas RBAC154-EMD05.pdf` | Esclarecimentos RBAC 154 |

## Implementação (concluída)

1. ✅ Normas RBAC-153-15 (SME), RBAC-153-16 (COE), RBAC-153-17 (PCM) adicionadas em `seed_data.py`
2. ✅ `getFunctionalArea` em `static/index.html` atualizado para mapear esses códigos às áreas SME, COE, PCM
3. ✅ `applies_to_types`: commercial, mixed, general_aviation | `min_passengers`: 200000 | `applies_to_sizes`: medium, large, international
4. ✅ Todas as normas RBAC-153 passaram a incluir `general_aviation` em `applies_to_types`

**Inferência a partir dos dados ANAC:** O compliance engine usa `usage_class` (I, II, III, IV) e `annual_passengers` (calculados a partir da busca ANAC) para determinar quais normas se aplicam. Aeroportos Classe II, III ou IV recebem automaticamente SME, COE e PCM ao executar "Verificar Conformidade".
