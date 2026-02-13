# Melhorias E2E e Otimizações

Resumo das correções e otimizações aplicadas ao fluxo de uso do sistema.

---

## Correções de Glitches E2E

### 1. **saveDueDate – Otimização**
- **Antes:** Fazia `POST /compliance/check` (verificação completa) só para obter as datas atuais do record.
- **Depois:** Usa `GET /compliance/records/{id}` para buscar apenas o record necessário.
- **Impacto:** Menos carga no servidor e resposta mais rápida ao salvar datas.

### 2. **saveNotes – Feedback em erro**
- **Antes:** Erro silencioso (apenas `console.error`).
- **Depois:** `showToast` em caso de falha.
- **Impacto:** Usuário percebe quando o salvamento falha.

### 3. **toggleActionItem – Proteção contra double-click**
- **Antes:** Cliques rápidos podiam disparar múltiplas requisições.
- **Depois:** Checkbox desabilitada durante a requisição; guarda por `recordId` evita chamadas concorrentes.
- **Impacto:** Evita estados inconsistentes e requisições duplicadas.

### 4. **saveCustomField – Proteção contra chamadas concorrentes**
- **Antes:** Alterações rápidas em vários campos (ex.: team_ba_ce, team_ba_lr) podiam sobrescrever umas às outras.
- **Depois:** Fila de pendências por `recordId`; se uma save está em andamento, a próxima é enfileirada e executada ao final.
- **Impacto:** Evita perda de dados em alterações rápidas.

### 5. **checkCompliance – Race condition**
- **Antes:** Duas verificações em sequência rápida podiam terminar fora de ordem.
- **Depois:** `AbortController` cancela a requisição anterior ao iniciar uma nova.
- **Impacto:** Resultado exibido corresponde sempre à última ação do usuário.

### 6. **Mensagem de erro de conexão**
- **Antes:** Texto fixo "http://localhost:8000".
- **Depois:** URL dinâmica com `window.location.origin`.
- **Impacto:** Mensagem correta em produção (ex.: Railway).

### 7. **autocomplete duplicado**
- **Antes:** `autocomplete="off" autocomplete="off"` no select de categoria.
- **Depois:** Apenas `autocomplete="off"`.
- **Impacto:** Código mais limpo e sem atributos redundantes.

---

## Fluxos já otimizados (anteriores)

- **Scroll ao salvar datas:** `preserveScroll: true` em `saveDueDate`.
- **Scroll ao marcar Conforme/Parcial:** `scrollToRecordId` em `toggleActionItem` e `updateStatus`.
- **Custom fields 422:** Envio de objeto em vez de string JSON.
- **DATABASE_PUBLIC_URL:** Prioridade para URL pública no Railway.

---

## Sugestões futuras

1. **Debounce em saveNotes:** `onblur` pode disparar várias vezes; considerar debounce de ~300 ms.
2. **Loading em saveCustomField:** Indicador visual durante o salvamento (ex.: spinner no campo).
3. **Retry automático:** Em erros de rede transitórios, oferecer "Tentar novamente".
4. **Offline:** Detectar ausência de rede e avisar antes de salvar.
