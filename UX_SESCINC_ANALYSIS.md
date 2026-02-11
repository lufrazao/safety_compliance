# Análise UX para Coordenador SESCINC

## Contexto
O coordenador SESCINC atualmente trabalha com **diversas planilhas** para registrar e acompanhar a conformidade com os requisitos da ANAC. O sistema precisa substituir esse fluxo de trabalho de forma eficiente.

## Análise do UX Atual

### ✅ O que o sistema já oferece:
1. **Registro de Status:** Conforme, Parcial, Não Conforme, Pendente
2. **Notas:** Campo de texto livre para observações
3. **Action Items:** Lista de itens de ação com datas de vencimento
4. **Filtros:** Por status, classificação, categoria
5. **Busca:** Por código ou título da norma
6. **Edição em Lote:** Para atualizar múltiplos registros
7. **Exportação:** Relatório em formato exportável
8. **Scores:** DOCS, TOPS e weighted score
9. **Histórico:** Registro de mudanças

### ❌ O que está faltando para substituir planilhas:

#### 1. **Campos Específicos SESCINC**
- [ ] **CAT do Aeródromo** (1-9) - Campo específico para registrar a categoria
- [ ] **Tempo-Resposta Medido** (em minutos) - Para RBAC-153-07
- [ ] **Data da Última Aferição** - Para tempo-resposta
- [ ] **Composição da Equipe** - Número de BA por função (BA-CE, BA-LR, BA-MC, BA-RE)
- [ ] **Especificações do CCI** - Capacidade água/espuma, número de veículos
- [ ] **Quantidade de Agentes Extintores** - Por tipo (AFFF, PQ, CO2)
- [ ] **Data de Validade de Certificações** - Para pessoal e equipamentos
- [ ] **Data de Próxima Manutenção** - Para CCI e equipamentos
- [ ] **Data de Próximo Treinamento** - Para PTR-BA

#### 2. **Upload de Documentos/Evidências**
- [ ] **Anexar documentos** (PDF, imagens) como evidência de conformidade
- [ ] **Certificados** (CBA-1, CBA-2, etc.)
- [ ] **Relatórios de Aferição** de tempo-resposta
- [ ] **Fotos** de equipamentos, instalações
- [ ] **PCINC** (Plano Contraincêndio)
- [ ] **Relatórios de Exercícios** simulados

#### 3. **Visualização Tipo Planilha**
- [ ] **Vista de tabela** (grid) similar a planilha Excel
- [ ] **Colunas customizáveis** (mostrar/ocultar)
- [ ] **Ordenação por múltiplas colunas**
- [ ] **Agrupamento** por classificação, categoria, status
- [ ] **Resumo por categoria** (D/C/B/A)

#### 4. **Gestão de Prazos e Alertas**
- [ ] **Dashboard de vencimentos** próximos
- [ ] **Alertas visuais** para itens próximos do vencimento
- [ ] **Notificações** de prazos críticos
- [ ] **Calendário** de eventos (aferições, treinamentos, manutenções)

#### 5. **Campos de Data Específicos**
- [ ] **Data de última verificação**
- [ ] **Data de próxima verificação**
- [ ] **Data de vencimento de certificação**
- [ ] **Data de validade de equipamento**
- [ ] **Data de exercício simulado**

#### 6. **Valores Numéricos Específicos**
- [ ] **Tempo-resposta** (minutos)
- [ ] **Número de BA** por função
- [ ] **Capacidade CCI** (litros água/espuma)
- [ ] **Quantidade de agentes** extintores
- [ ] **Número de veículos** (CCI, CACE, CRS)

#### 7. **Melhorias na Interface**
- [ ] **Formulário expandido** para cada norma com todos os campos
- [ ] **Campos condicionais** (mostrar apenas campos relevantes para cada norma)
- [ ] **Validação de dados** (ex: tempo-resposta ≤ 3min)
- [ ] **Indicadores visuais** de conformidade mais claros
- [ ] **Progresso visual** por categoria (D/C/B/A)

## Comparação: Planilhas vs. Sistema Atual

### Trabalho com Planilhas (Atual)
✅ **Vantagens:**
- Flexibilidade total para adicionar colunas
- Fácil visualização em formato tabular
- Fácil compartilhamento
- Fácil impressão
- Fórmulas e cálculos automáticos

❌ **Desvantagens:**
- Sem validação de dados
- Sem histórico de mudanças
- Sem controle de versão
- Difícil colaboração simultânea
- Sem integração com outros sistemas
- Sem alertas automáticos

### Sistema Atual
✅ **Vantagens:**
- Histórico de mudanças
- Validação de dados
- Colaboração simultânea
- Integração com backend
- Alertas e notificações (parcial)
- Exportação de relatórios

❌ **Desvantagens:**
- Falta de campos específicos SESCINC
- Sem upload de documentos
- Sem visualização tipo planilha
- Campos limitados (apenas status, notas, action items)
- Sem gestão de prazos visual

## Recomendações Prioritárias

### Prioridade ALTA (Essencial para substituir planilhas)

1. **Campos Específicos SESCINC**
   - Adicionar campos customizados por tipo de norma
   - Exemplo: Para RBAC-153-07, adicionar campo "Tempo-Resposta (min)"
   - Exemplo: Para RBAC-153-01, adicionar campo "CAT do Aeródromo"

2. **Upload de Documentos**
   - Permitir anexar arquivos como evidência
   - Tipos: PDF, imagens, documentos
   - Limite de tamanho e quantidade

3. **Vista de Tabela/Planilha**
   - Opção de visualização em grid
   - Colunas: Código, Título, Status, CAT, Tempo-Resposta, Última Verificação, etc.
   - Exportação para Excel mantendo formatação

4. **Gestão de Prazos**
   - Dashboard de vencimentos
   - Alertas visuais (cores, ícones)
   - Filtro por "próximos a vencer"

### Prioridade MÉDIA

5. **Campos de Data Específicos**
   - Data de última aferição
   - Data de próxima manutenção
   - Data de vencimento de certificação

6. **Valores Numéricos**
   - Campos para valores específicos (tempo-resposta, quantidade, etc.)
   - Validação automática (ex: tempo ≤ 3min)

7. **Formulário Expandido**
   - Modal ou seção expandida com todos os campos
   - Campos condicionais baseados no tipo de norma

### Prioridade BAIXA

8. **Calendário de Eventos**
9. **Agrupamento Avançado**
10. **Colunas Customizáveis**

## Proposta de Implementação

### Fase 1: Campos Específicos SESCINC
- Adicionar campos customizados no modelo `ComplianceRecord`
- Criar interface para preencher campos específicos por norma
- Validação de dados específicos

### Fase 2: Upload de Documentos
- Sistema de armazenamento de arquivos
- Interface de upload e visualização
- Integração com registros de conformidade

### Fase 3: Vista de Planilha
- Componente de tabela/grid
- Exportação aprimorada para Excel
- Filtros e ordenação avançados

### Fase 4: Gestão de Prazos
- Dashboard de vencimentos
- Sistema de alertas
- Notificações automáticas

## Conclusão

O sistema atual **tem uma boa base**, mas precisa de **melhorias específicas** para substituir completamente o trabalho com planilhas. As principais lacunas são:

1. **Campos específicos** para dados SESCINC (CAT, tempo-resposta, etc.)
2. **Upload de documentos** como evidência
3. **Visualização tipo planilha** para familiaridade
4. **Gestão de prazos** visual e alertas

Com essas melhorias, o sistema será **superior às planilhas** mantendo a flexibilidade e adicionando controle, histórico e colaboração.
