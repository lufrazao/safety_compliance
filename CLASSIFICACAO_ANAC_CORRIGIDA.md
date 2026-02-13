# Correção das Classificações de Aeroportos - ANAC

## Problema Identificado

A classificação de categorias de aeroportos estava incorreta. O sistema usava categorias 1C-9C que não correspondem às classificações oficiais da ANAC.

## Classificações Corretas da ANAC

### 1. Por Uso (RBAC 153)
- **Classe I**: Público - < 200 mil passageiros/ano
- **Classe II**: Público - 200 mil - 1 milhão passageiros/ano
- **Classe III**: Público - 1 milhão - 5 milhões passageiros/ano
- **Classe IV**: Público - > 5 milhões passageiros/ano
- **Privado**: Uso restrito ao proprietário, sem exploração comercial

### 2. Classificação AVSEC (Segurança contra Atos de Interferência Ilícita)
- **AP-0**: Aviação geral/táxi aéreo/fretamento
- **AP-1**: Comercial regular/charter, < 600 mil pass./ano
- **AP-2**: Comercial regular/charter, 600 mil - 5 milhões pass./ano
- **AP-3**: Comercial regular/charter, > 5 milhões pass./ano

### 3. Quanto ao Porte da Aeronave (Avaliação de Pista)
- **A/B**: Aeronaves até 5.700 kg
- **C**: Aeronaves entre 5.700 kg e 136.000 kg
- **D**: Aeronaves acima de 136.000 kg

## Alterações Implementadas

### Backend

1. **Novos Enums Criados** (`app/models.py`):
   - `AirportUsageClass`: I, II, III, IV, PRIVADO
   - `AVSECClassification`: AP-0, AP-1, AP-2, AP-3
   - `AircraftSizeCategory`: A/B, C, D

2. **Modelo Airport Atualizado**:
   - Removido: `category` (antigo campo 1C-9C)
   - Adicionado: `usage_class` (Classe por uso RBAC 153)
   - Adicionado: `avsec_classification` (Classificação AVSEC)
   - Adicionado: `aircraft_size_category` (Categoria de porte da aeronave)
   - Mantido: `reference_code` (para compatibilidade)

3. **Schemas Atualizados** (`app/schemas.py`):
   - `AirportBase` atualizado com os novos campos
   - Imports atualizados para incluir os novos enums

4. **Migração de Banco de Dados**:
   - Script `migrations/update_airport_classifications.py` criado
   - Migração executada com sucesso
   - Dados existentes migrados automaticamente

### Frontend

1. **Formulário de Cadastro Atualizado** (`static/index.html`):
   - Removido: Campo "Categoria do Aeroporto (ANAC)" com opções 1C-9C
   - Adicionado: Campo "Classe por Uso (RBAC 153)" com opções I, II, III, IV, PRIVADO
   - Adicionado: Campo "Classificação AVSEC" com opções AP-0, AP-1, AP-2, AP-3
   - Adicionado: Campo "Categoria de Porte da Aeronave" com opções A/B, C, D
   - Campo "Passageiros Anuais" agora calcula automaticamente as classificações

2. **Função de Cálculo Automático**:
   - `calculateANACClassifications()` implementada
   - Calcula automaticamente:
     - Classe por Uso baseada em passageiros anuais
     - Classificação AVSEC baseada em passageiros anuais
     - Categoria de Porte baseada em peso máximo de aeronave

3. **Funções Atualizadas**:
   - `saveAirport()`: Usa os novos campos
   - `editAirport()`: Carrega os novos campos
   - `saveDraft()`: Salva os novos campos
   - `loadDraft()`: Carrega os novos campos (com compatibilidade retroativa)
   - `displayAirportList()`: Exibe as novas classificações

4. **Visualizações Atualizadas**:
   - Dashboard: Exibe Classe e AVSEC
   - Lista de Aeroportos: Exibe badges com as classificações
   - Relatórios: Incluem as novas classificações

## Lógica de Cálculo Automático

### Classe por Uso (RBAC 153)
```javascript
if (passengers < 200000) → Classe I
else if (passengers < 1000000) → Classe II
else if (passengers < 5000000) → Classe III
else → Classe IV
```

### Classificação AVSEC
```javascript
if (passengers < 600000) → AP-1
else if (passengers < 5000000) → AP-2
else → AP-3
```

### Categoria de Porte da Aeronave
```javascript
if (maxWeightKg <= 5700) → A/B
else if (maxWeightKg <= 136000) → C
else → D
```

## Compatibilidade

- O campo `reference_code` foi mantido para compatibilidade
- A migração preserva dados existentes
- Funções de draft incluem compatibilidade retroativa

## Status

✅ **Implementação Completa**
- Backend atualizado
- Frontend atualizado
- Migração executada
- Cálculo automático funcionando
- Visualizações atualizadas
