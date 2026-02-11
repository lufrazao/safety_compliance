# Proposta de Melhorias UX para Coordenador SESCINC

## Resposta Direta

**NÃO, o UX atual não é ideal** para substituir completamente as planilhas que o coordenador SESCINC utiliza. O sistema tem uma boa base, mas faltam recursos essenciais para um fluxo de trabalho eficiente.

## Problemas Identificados

### 1. ❌ Falta de Campos Específicos SESCINC
**Problema:** O sistema só tem campos genéricos (status, notas, action items). Faltam campos específicos que o coordenador precisa registrar:
- CAT do aeródromo (1-9)
- Tempo-resposta medido (em minutos)
- Data da última aferição
- Composição da equipe (número de BA por função)
- Especificações do CCI (capacidade água/espuma)
- Quantidade de agentes extintores
- Datas de vencimento de certificações

**Impacto:** O coordenador ainda precisa usar planilhas para registrar esses dados específicos.

### 2. ❌ Sem Upload de Documentos
**Problema:** Não é possível anexar documentos como evidência:
- Certificados (CBA-1, CBA-2, etc.)
- Relatórios de aferição de tempo-resposta
- PCINC (Plano Contraincêndio)
- Fotos de equipamentos
- Relatórios de exercícios simulados

**Impacto:** Documentos ficam em pastas separadas, dificultando auditoria e verificação.

### 3. ❌ Sem Visualização Tipo Planilha
**Problema:** A visualização atual é em cards, não em tabela. O coordenador está acostumado com formato de planilha onde pode ver tudo de uma vez.

**Impacto:** Dificulta comparação rápida entre normas e visualização geral do status.

### 4. ❌ Gestão de Prazos Limitada
**Problema:** Existe gestão de prazos para action items, mas não para:
- Vencimento de certificações
- Próxima aferição de tempo-resposta
- Próxima manutenção de CCI
- Próximo treinamento PTR-BA

**Impacto:** Risco de esquecer prazos importantes e não conformidade.

## O que o Sistema JÁ FAZ BEM

✅ **Registro de Status:** Fácil marcar conforme/parcial/não conforme
✅ **Filtros e Busca:** Encontrar normas rapidamente
✅ **Edição em Lote:** Atualizar múltiplos registros
✅ **Histórico:** Rastreamento de mudanças
✅ **Action Items:** Gestão de tarefas com datas
✅ **Exportação:** Gerar relatórios

## Proposta de Melhorias Prioritárias

### 🚀 FASE 1: Campos Específicos SESCINC (CRÍTICO)

Adicionar campos customizados que aparecem condicionalmente baseado no código da norma:

#### Para RBAC-153-01 (Determinação da CAT):
- Campo: "CAT do Aeródromo" (dropdown 1-9)
- Campo: "Data de Determinação"
- Campo: "Data de Última Revisão"

#### Para RBAC-153-07 (Tempo-Resposta):
- Campo: "Tempo-Resposta Medido" (número em minutos)
- Campo: "Data da Última Aferição"
- Campo: "Data da Próxima Aferição"
- Campo: "Ponto Crítico Testado" (texto)
- Validação: Alertar se > 3 minutos

#### Para RBAC-153-06 (Equipe de Serviço):
- Campo: "Número de BA-CE" (Chefe de Equipe)
- Campo: "Número de BA-LR" (Líder de Resgate)
- Campo: "Número de BA-MC" (Motorista/Operador)
- Campo: "Número de BA-RE" (Resgatista)
- Campo: "Total de BA na Equipe"

#### Para RBAC-153-04 (CCI):
- Campo: "Número de CCI"
- Campo: "Capacidade de Água (litros)"
- Campo: "Capacidade de Espuma (litros)"
- Campo: "Data da Última Manutenção"
- Campo: "Data da Próxima Manutenção"

#### Para RBAC-153-03 (Agentes Extintores):
- Campo: "Quantidade AFFF (litros)"
- Campo: "Quantidade Pó Químico (kg)"
- Campo: "Quantidade CO2 (kg)"
- Campo: "Data de Validade Mais Próxima"

#### Para RBAC-153-08 (Capacitação):
- Campo: "Número de BA com CBA-1"
- Campo: "Número de BA com CBA-2"
- Campo: "Número de BA com CBA-AT (válido)"
- Campo: "Data do Próximo Treinamento"

### 🚀 FASE 2: Upload de Documentos (CRÍTICO)

- Botão "Anexar Documentos" em cada registro
- Tipos aceitos: PDF, JPG, PNG, DOC, DOCX
- Limite: 5 arquivos por registro, 10MB cada
- Visualização: Lista de documentos anexados com opção de download/excluir
- Categorias: Certificado, Relatório, Foto, Outro

### 🚀 FASE 3: Vista de Planilha (ALTA PRIORIDADE)

- Botão "Vista de Tabela" / "Vista de Cards" (toggle)
- Colunas na tabela:
  - Código | Título | Status | CAT | Tempo-Resposta | Última Verificação | Próxima Ação | Documentos
- Ordenação clicável nas colunas
- Exportação para Excel com formatação
- Filtros mantidos na vista de tabela

### 🚀 FASE 4: Dashboard de Vencimentos (ALTA PRIORIDADE)

- Seção "Próximos Vencimentos" no topo
- Cards com:
  - Certificações vencendo em 30 dias
  - Aferições de tempo-resposta pendentes
  - Manutenções de CCI próximas
  - Treinamentos PTR-BA agendados
- Contador de itens críticos
- Link direto para cada item

## Implementação Sugerida

### Opção 1: Campos Customizados via JSON
Adicionar campo `custom_fields` no `ComplianceRecord` que armazena JSON com campos específicos:
```json
{
  "fire_category": 5,
  "response_time_minutes": 2.5,
  "last_response_test_date": "2025-01-15",
  "team_composition": {
    "ba_ce": 1,
    "ba_lr": 1,
    "ba_mc": 2,
    "ba_re": 3
  }
}
```

### Opção 2: Campos Específicos no Modelo
Adicionar colunas específicas no banco de dados para os campos mais usados.

**Recomendação:** Opção 1 (JSON) para flexibilidade, com interface que renderiza campos baseado no código da norma.

## Comparação: Antes vs. Depois

### ANTES (Sistema Atual)
- ❌ Coordenador precisa usar planilhas para dados específicos
- ❌ Documentos ficam em pastas separadas
- ❌ Visualização limitada (só cards)
- ❌ Sem alertas de prazos específicos SESCINC

### DEPOIS (Com Melhorias)
- ✅ Todos os dados SESCINC no sistema
- ✅ Documentos anexados como evidência
- ✅ Visualização tipo planilha familiar
- ✅ Alertas automáticos de prazos
- ✅ **Substituição completa das planilhas**

## Próximos Passos

1. **Decisão:** Qual abordagem usar para campos customizados?
2. **Priorização:** Qual fase implementar primeiro?
3. **Prototipagem:** Criar mockup da interface melhorada
4. **Implementação:** Desenvolver melhorias em fases

## Conclusão

O sistema atual é uma **boa base**, mas precisa de **melhorias específicas** para ser uma alternativa viável às planilhas. As 4 fases propostas transformarão o sistema em uma ferramenta superior, mantendo a flexibilidade das planilhas e adicionando controle, histórico e colaboração.

**Recomendação:** Implementar Fase 1 (Campos Específicos) e Fase 2 (Upload) primeiro, pois são as mais críticas para substituir planilhas.
