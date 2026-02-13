# Plano de Ação: Melhorias para Gestão de Áreas SESCINC

## 🎯 Objetivo
Implementar todas as melhorias identificadas para que o sistema ajude da melhor forma o gestor SESCINC a gerenciar as diferentes áreas funcionais.

## 📋 Ordem de Implementação

### FASE 1: Estrutura Base (Fundação) ⚙️
**Prioridade: CRÍTICA**
**Tempo estimado: 2-3 horas**

1. ✅ **Mapeamento de Áreas Funcionais**
   - Criar função para mapear normas RBAC-153 para áreas funcionais
   - Definir estrutura de dados para áreas
   - Atualizar seed_data.py com mapeamento de áreas

2. ✅ **Modelo de Dados para Áreas**
   - Adicionar campo `functional_area` ao modelo Regulation (opcional)
   - Criar função helper para identificar área funcional por código

3. ✅ **Agrupamento por Área Funcional**
   - Modificar displayCompliance para agrupar por área funcional
   - Manter agrupamento por RBAC como secundário
   - Criar banners visuais por área

### FASE 2: Dashboard por Área (Visualização) 📊
**Prioridade: CRÍTICA**
**Tempo estimado: 2-3 horas**

4. ✅ **Dashboard de Áreas Funcionais**
   - Criar novo tab "Áreas SESCINC" no dashboard
   - Cards por área com status consolidado
   - Indicadores: % conforme, prazos próximos, documentos

5. ✅ **Navegação por Área**
   - Filtro rápido por área funcional
   - Breadcrumbs atualizados para incluir área
   - Links diretos para cada área

### FASE 3: Upload de Documentos 📎
**Prioridade: ALTA**
**Tempo estimado: 3-4 horas**

6. ✅ **Backend: Armazenamento de Documentos**
   - Criar modelo DocumentAttachment
   - Endpoints: upload, list, download, delete
   - Integração com ComplianceRecord

7. ✅ **Frontend: Interface de Upload**
   - Botão "Anexar Documentos" em cada norma
   - Drag & drop ou seleção de arquivos
   - Preview e lista de documentos anexados
   - Categorização por tipo (Certificado, Relatório, Foto, Outro)

### FASE 4: Vista de Planilha/Tabela 📈
**Prioridade: ALTA**
**Tempo estimado: 2-3 horas**

8. ✅ **Toggle Cards/Tabela**
   - Botão para alternar visualização
   - Componente de tabela responsivo
   - Colunas customizáveis por área

9. ✅ **Exportação Aprimorada**
   - Exportação para Excel mantendo estrutura por área
   - Formatação condicional
   - Múltiplas abas por área

### FASE 5: Gestão de Prazos por Área 📅
**Prioridade: ALTA**
**Tempo estimado: 2-3 horas**

10. ✅ **Dashboard de Prazos**
    - Seção "Prazos Próximos" no dashboard
    - Agrupamento por área funcional
    - Alertas visuais (cores, ícones)

11. ✅ **Calendário de Eventos**
    - Visualização mensal de eventos por área
    - Filtro por tipo de prazo (aferição, manutenção, treinamento)
    - Exportação para calendário externo

### FASE 6: Relatórios por Área 📄
**Prioridade: MÉDIA**
**Tempo estimado: 2 horas**

12. ✅ **Gerador de Relatórios por Área**
    - Template de relatório por área funcional
    - Inclusão de documentos anexados
    - Gráficos e métricas por área
    - Exportação PDF/Excel

### FASE 7: Indicadores de Performance 📊
**Prioridade: MÉDIA**
**Tempo estimado: 2-3 horas**

13. ✅ **KPIs por Área**
    - Cards de métricas no dashboard
    - Gráficos de evolução temporal
    - Comparação entre áreas
    - Alertas automáticos

### FASE 8: Melhorias de UX 🎨
**Prioridade: BAIXA**
**Tempo estimado: 1-2 horas**

14. ✅ **Biblioteca de Documentos Centralizada**
    - Página dedicada para documentos
    - Busca e filtros avançados
    - Organização por área/norma

15. ✅ **Validações e Alertas**
    - Validação de dados específicos (ex: tempo ≤ 3min)
    - Alertas visuais para não conformidades
    - Sugestões automáticas

## 📊 Mapeamento de Áreas Funcionais

### Áreas Identificadas:

1. **Gestão da CAT** (Categoria Contraincêndio)
   - RBAC-153-01: Determinação da CAT
   - RBAC-153-02: Operações Compatíveis com a CAT

2. **Gestão de Equipamentos**
   - RBAC-153-03: Agentes Extintores
   - RBAC-153-04: Carro Contraincêndio (CCI)
   - RBAC-153-05: Veículos de Apoio
   - RBAC-153-09: Equipamentos de Uso

3. **Gestão de Recursos Humanos**
   - RBAC-153-06: Equipe de Serviço
   - RBAC-153-08: Capacitação
   - RBAC-153-10: Programa PTR-BA

4. **Gestão Operacional**
   - RBAC-153-07: Tempo-Resposta
   - RBAC-153-11: Plano Contraincêndio (PCINC)

5. **Gestão de Infraestrutura**
   - RBAC-153-12: Infraestrutura da SCI
   - RBAC-153-13: Posto Avançado (PACI)

6. **Gestão de Documentação**
   - RBAC-153-14: Informações ao Órgão Regulador

## 🚀 Início da Implementação

Vou começar pela FASE 1 (Estrutura Base) e seguir a ordem do plano.
