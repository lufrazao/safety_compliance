# Correção: Filtragem por Aeroporto nas Abas de Prazos e Áreas

## 🔍 Problema Identificado

Ao selecionar um aeroporto para verificação de conformidade, as abas de **Prazos** e **Áreas SESCINC** não estavam sendo atualizadas automaticamente com os dados do aeroporto selecionado.

## ✅ Solução Implementada

### 1. **Variável Global para Rastrear Aeroporto Selecionado**

Adicionada variável `window.selectedAirportId` para armazenar o ID do aeroporto selecionado, permitindo que todas as abas acessem essa informação.

```javascript
// Initialize airport selection tracking
window.selectedAirportId = null;
```

### 2. **Atualização das Funções `loadDeadlines()` e `loadAreas()`**

Modificadas para verificar tanto o `airportSelect` quanto `window.selectedAirportId`:

```javascript
// Get selected airport - check both airportSelect and window.selectedAirportId
const airportSelect = document.getElementById('airportSelect');
let airportId = null;

if (airportSelect && airportSelect.value) {
    airportId = parseInt(airportSelect.value);
} else if (window.selectedAirportId) {
    airportId = parseInt(window.selectedAirportId);
}
```

### 3. **Event Listener no Select de Aeroporto**

Adicionado listener no `airportSelect` para atualizar automaticamente as outras abas quando um aeroporto é selecionado:

```javascript
select.addEventListener('change', function() {
    const airportId = this.value;
    if (airportId) {
        // Store selected airport ID for other tabs to use
        window.selectedAirportId = airportId;
        
        // If deadlines or areas tabs are active, reload them
        const deadlinesTab = document.getElementById('deadlinesTab');
        const areasTab = document.getElementById('areasTab');
        
        if (deadlinesTab && deadlinesTab.classList.contains('active')) {
            loadDeadlines();
        }
        if (areasTab && areasTab.classList.contains('active')) {
            loadAreas();
        }
    } else {
        window.selectedAirportId = null;
    }
});
```

### 4. **Atualização na Função `checkCompliance()`**

Modificada para armazenar o `selectedAirportId` e atualizar as outras abas após verificar conformidade:

```javascript
// Store selected airport ID for other tabs
window.selectedAirportId = airportId;

// Update other tabs if they are active
const deadlinesTab = document.getElementById('deadlinesTab');
const areasTab = document.getElementById('areasTab');

if (deadlinesTab && deadlinesTab.classList.contains('active')) {
    loadDeadlines();
}
if (areasTab && areasTab.classList.contains('active')) {
    loadAreas();
}
```

### 5. **Atualização na Função `viewAirportCompliance()`**

Modificada para armazenar o `selectedAirportId` quando um aeroporto é selecionado do dashboard:

```javascript
// Store selected airport ID for other tabs
window.selectedAirportId = airportId;
```

## 🔄 Fluxo de Funcionamento

1. **Usuário seleciona aeroporto na aba "Verificar Conformidade"**
   - `airportSelect.value` é atualizado
   - `window.selectedAirportId` é armazenado
   - Event listener detecta mudança

2. **Se abas "Prazos" ou "Áreas" estiverem ativas**
   - Funções `loadDeadlines()` ou `loadAreas()` são chamadas automaticamente
   - Dados são filtrados pelo aeroporto selecionado

3. **Usuário clica em "Verificar Conformidade"**
   - `checkCompliance()` é executado
   - `window.selectedAirportId` é atualizado
   - Se outras abas estiverem ativas, são atualizadas automaticamente

4. **Usuário navega para outras abas**
   - `loadDeadlines()` e `loadAreas()` verificam `window.selectedAirportId`
   - Se houver aeroporto selecionado, carregam dados filtrados
   - Se não houver, mostram mensagem para selecionar aeroporto

## 📋 Comportamento Esperado

### Aba "Verificar Conformidade"
- ✅ Mostra conformidades do aeroporto selecionado
- ✅ Atualiza `window.selectedAirportId` quando aeroporto é selecionado

### Aba "Prazos"
- ✅ Mostra prazos e vencimentos do aeroporto selecionado
- ✅ Se nenhum aeroporto estiver selecionado, mostra mensagem para selecionar
- ✅ Atualiza automaticamente quando aeroporto é selecionado em outra aba

### Aba "Áreas SESCINC"
- ✅ Mostra áreas funcionais do aeroporto selecionado
- ✅ Se nenhum aeroporto estiver selecionado, mostra mensagem para selecionar
- ✅ Atualiza automaticamente quando aeroporto é selecionado em outra aba

## 🎯 Benefícios

1. **Consistência**: Todas as abas mostram dados do mesmo aeroporto
2. **Sincronização**: Seleção de aeroporto em uma aba atualiza as outras
3. **UX Melhorada**: Usuário não precisa selecionar aeroporto em cada aba
4. **Feedback Visual**: Mensagens claras quando nenhum aeroporto está selecionado

## ✅ Testes Recomendados

1. Selecionar aeroporto na aba "Verificar Conformidade" → Verificar se "Prazos" e "Áreas" atualizam
2. Navegar para "Prazos" sem selecionar aeroporto → Verificar mensagem de seleção
3. Selecionar aeroporto e navegar entre abas → Verificar que dados são consistentes
4. Selecionar aeroporto do dashboard → Verificar se todas as abas atualizam
