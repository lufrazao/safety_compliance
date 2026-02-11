# Análise: RBAC-153 para SESCINC

## Resumo Executivo

O sistema atualmente utiliza **apenas RBAC-154** para todas as normas. No entanto, para a área de **SESCINC (Serviço de Salvamento e Combate a Incêndio em Aeródromos Civis)**, o sistema deve também incluir **RBAC-153**, conforme estabelecido no documento "Curso Básico de Gestão do SESCINC" da Infraero.

## Situação Atual

### Regulamentos Existentes (RBAC-154)
- ✅ RBAC-154-10: Serviço de Combate a Incêndio e Resgate (SCIR)
- ✅ RBAC-154-11: Equipamentos de Combate a Incêndio
- ✅ RBAC-154-12: Categoria de SCIR por Tamanho de Aeronave
- ✅ RBAC-154-13: Sistema de Detecção e Alarme de Incêndio

### Problema Identificado
O sistema está usando **RBAC-154** para requisitos de combate a incêndio, mas **RBAC-153** é o regulamento específico que estabelece:
- Requisitos obrigatórios de capacitação para bombeiros de aeródromo
- Gestão do SESCINC
- Categorização contraincêndio (CAT)
- Equipamentos e veículos (CCI)
- Tempo-resposta
- Plano Contraincêndio de Aeródromo (PCINC)

## Requisitos RBAC-153 Identificados no Documento SESCINC

Com base na apostila "Curso Básico de Gestão do SESCINC", os seguintes requisitos devem ser adicionados:

### 1. Determinação da CAT (Categoria Contraincêndio)
- **RBAC-153-01**: Determinação da CAT do Aeródromo
  - Baseada na maior aeronave que opera regularmente
  - Categorias de 1 a 9
  - Aplicável a todos os aeroportos comerciais

### 2. Operações Compatíveis com a CAT
- **RBAC-153-02**: Operações Compatíveis com a CAT
  - Restrições de operação baseadas na categoria
  - Notificação quando aeronave maior que a CAT operar

### 3. Agentes Extintores
- **RBAC-153-03**: Agentes Extintores para Combate a Incêndio
  - Espuma AFFF (Aqueous Film Forming Foum)
  - Pó Químico (PQ)
  - Gás Carbônico (CO2)
  - Especificações e quantidades mínimas

### 4. Carro Contraincêndio de Aeródromo (CCI)
- **RBAC-153-04**: Carro Contraincêndio de Aeródromo (CCI)
  - Especificações técnicas conforme categoria
  - Capacidade de água e espuma
  - Velocidade mínima
  - Certificação e manutenção

### 5. Veículos de Apoio
- **RBAC-153-05**: Veículos de Apoio ao SESCINC
  - Carro de Apoio ao Chefe de Equipe (CACE)
  - Carro de Resgate e Salvamento (CRS)
  - Outros veículos conforme necessidade

### 6. Equipe de Serviço do SESCINC
- **RBAC-153-06**: Equipe de Serviço do SESCINC
  - Composição mínima por categoria
  - Funções: BA-CE, BA-LR, BA-MC, BA-RE
  - Disponibilidade 24/7 para aeroportos comerciais

### 7. Tempo-Resposta
- **RBAC-153-07**: Procedimento para Aferição de Tempo-Resposta
  - Tempo máximo de 3 minutos para aeroportos comerciais
  - Aferição regular
  - Registro e documentação

### 8. Capacitação de Recursos Humanos
- **RBAC-153-08**: Capacitação de Recursos Humanos para o SESCINC
  - CBA-1: Curso de Habilitação de Bombeiro de Aeródromo 1
  - CBA-2: Curso de Habilitação de Bombeiro de Aeródromo 2
  - CBA-AT: Curso de Atualização
  - CBA-CE: Curso de Especialização Chefe de Equipe
  - CBA-MC: Curso de Especialização Motorista/Operador de CCI
  - PTR-BA: Programa de Treinamento Recorrente

### 9. Equipamentos de Uso do SESCINC
- **RBAC-153-09**: Equipamentos de Uso do SESCINC
  - EPI (Equipamento de Proteção Individual)
  - EPR (Equipamento de Proteção Respiratória)
  - TP (Traje de Proteção)
  - Ferramentas de resgate
  - Equipamentos médicos básicos

### 10. Programa de Treinamento Recorrente (PTR-BA)
- **RBAC-153-10**: Programa de Treinamento Recorrente para Bombeiro de Aeródromo
  - Treinamento teórico e prático
  - Frequência mínima (anual)
  - Registro de treinamentos
  - Avaliação de desempenho

### 11. Plano Contraincêndio de Aeródromo (PCINC)
- **RBAC-153-11**: Plano Contraincêndio de Aeródromo (PCINC)
  - Documento obrigatório
  - Conteúdo mínimo conforme RBAC-153
  - Atualização periódica
  - Exercícios simulados

### 12. Infraestrutura SCI e PACI
- **RBAC-153-12**: Infraestrutura da Seção Contraincêndio (SCI)
  - Localização estratégica
  - Dimensões mínimas
  - Equipamentos e facilidades
- **RBAC-153-13**: Posto Avançado de Contraincêndio (PACI)
  - Para aeroportos grandes/internacionais
  - Localização em pontos estratégicos
  - Equipamentos básicos

### 13. Informações ao Órgão Regulador
- **RBAC-153-14**: Informações ao Órgão Regulador (ANAC)
  - Notificação de mudanças na CAT
  - Relatórios de exercícios
  - Atualização de PCINC
  - Registro de incidentes

## Classificação ANAC (D/C/B/A)

### D - Essenciais (Peso 8-10)
- RBAC-153-01: Determinação da CAT (D, peso 10)
- RBAC-153-04: CCI adequado à categoria (D, peso 10)
- RBAC-153-06: Equipe de serviço do SESCINC (D, peso 10)
- RBAC-153-07: Tempo-resposta ≤ 3min (D, peso 10)
- RBAC-153-08: Capacitação obrigatória (D, peso 9)
- RBAC-153-11: PCINC documentado (D, peso 9)

### C - Complementares (Peso 5-7)
- RBAC-153-02: Operações compatíveis com CAT (C, peso 7)
- RBAC-153-03: Agentes extintores (C, peso 7)
- RBAC-153-05: Veículos de apoio (C, peso 6)
- RBAC-153-09: Equipamentos de uso (C, peso 6)
- RBAC-153-10: PTR-BA implementado (C, peso 7)
- RBAC-153-12: Infraestrutura SCI (C, peso 6)
- RBAC-153-14: Informações à ANAC (C, peso 6)

### B - Recomendadas (Peso 3-4)
- RBAC-153-13: PACI para grandes aeroportos (B, peso 4)

## Aplicabilidade por Tipo de Aeroporto

### Todos os Aeroportos Comerciais
- RBAC-153-01: Determinação da CAT
- RBAC-153-04: CCI adequado
- RBAC-153-06: Equipe de serviço
- RBAC-153-07: Tempo-resposta
- RBAC-153-08: Capacitação
- RBAC-153-11: PCINC

### Aeroportos Médios/Grandes (200k+ passageiros)
- RBAC-153-02: Operações compatíveis
- RBAC-153-03: Agentes extintores
- RBAC-153-05: Veículos de apoio
- RBAC-153-09: Equipamentos
- RBAC-153-10: PTR-BA
- RBAC-153-12: Infraestrutura SCI

### Aeroportos Grandes/Internacionais (1M+ passageiros)
- RBAC-153-13: PACI

## Próximos Passos

1. ✅ Adicionar regulamentos RBAC-153 ao `seed_data.py`
2. ✅ Atualizar `compliance_engine.py` para reconhecer RBAC-153
3. ✅ Garantir que a lógica de aplicabilidade funcione para ambos RBAC-153 e RBAC-154
4. ✅ Atualizar documentação do sistema

## Referências

- RBAC-153: Regulamento Brasileiro de Aviação Civil nº 153
- Apostila: Curso Básico de Gestão do SESCINC - Infraero (2ª edição, 2023)
- RBAC-154: Regulamento Brasileiro de Aviação Civil nº 154
