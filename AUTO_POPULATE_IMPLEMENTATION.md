# Implementação: Preenchimento Automático de Dados de Aeroporto

## ✅ O que foi implementado

### 1. **Backend: Endpoint de Busca por Código ICAO**

**Endpoint:** `GET /api/airports/lookup/{icao_code}`

**Funcionalidades:**
- Busca um aeroporto específico na lista oficial da ANAC
- Retorna dados que podem preencher o formulário automaticamente
- Calcula campos derivados (usage_class, avsec_classification, aircraft_size_category)

**Campos retornados:**
- `name`: Nome oficial do aeródromo
- `code`: Código ICAO
- `iata_code`: Código IATA (se disponível)
- `city`: Cidade
- `state`: Estado (UF)
- `latitude`: Latitude
- `longitude`: Longitude
- `reference_code`: Código de referência das aeronaves
- `status`: Status operacional
- `usage_class`: Calculado baseado na categoria
- `avsec_classification`: Calculado baseado em passageiros estimados
- `aircraft_size_category`: Inferido do reference_code

### 2. **Frontend: Botão de Busca e Preenchimento Automático**

**Localização:** Formulário de cadastro de aeroporto, ao lado do campo "Código ICAO"

**Funcionalidades:**
- Botão "🔍 Buscar da ANAC" habilitado quando código ICAO tem 4 letras válidas
- Busca dados da ANAC ao clicar
- Preenche automaticamente os campos disponíveis
- Mostra status visual da busca (buscando, sucesso, erro)
- Permite edição manual após preenchimento automático

**Campos preenchidos automaticamente:**
- ✅ Nome do aeroporto
- ✅ Código de referência das aeronaves
- ✅ Classe por Uso (usage_class) - calculado
- ✅ Classificação AVSEC - calculado
- ✅ Categoria de Porte da Aeronave - inferido

## 📋 Campos que Podem Ser Preenchidos Automaticamente

### Diretos da ANAC:
1. **Nome oficial** - `name`
2. **Código ICAO** - `code` (já digitado pelo usuário)
3. **Código IATA** - `iata_code` (se disponível)
4. **Cidade** - `city`
5. **Estado (UF)** - `state`
6. **Latitude/Longitude** - `latitude`, `longitude`
7. **Código de Referência** - `reference_code` (se disponível)
8. **Status Operacional** - `status`

### Calculados/Inferidos:
1. **Usage Class (Classe por Uso)**
   - Baseado na categoria ANAC (1C-9C)
   - Categoria 1-2 → Classe I
   - Categoria 3-4 → Classe II
   - Categoria 5-6 → Classe III
   - Categoria 7-9 → Classe IV

2. **AVSEC Classification**
   - Baseado em passageiros anuais estimados
   - < 600k → AP-1
   - 600k - 5M → AP-2
   - > 5M → AP-3

3. **Aircraft Size Category**
   - Inferido do código de referência
   - Última letra do reference_code:
     - A/B → A/B
     - C → C
     - D/E → D

4. **Size** (calculado automaticamente)
   - Baseado em usage_class
   - PRIVADO/I → SMALL
   - II → MEDIUM
   - III → LARGE
   - IV → INTERNATIONAL

5. **Annual Passengers** (estimativa)
   - Baseado em usage_class
   - I → 100k
   - II → 600k
   - III → 3M
   - IV → 10M

## 🔄 Fluxo de Uso

1. **Usuário digita código ICAO** (ex: SBGR)
   - Botão "Buscar da ANAC" é habilitado automaticamente

2. **Usuário clica "🔍 Buscar da ANAC"**
   - Sistema busca na lista oficial da ANAC
   - Mostra status "Buscando..."

3. **Sistema preenche campos automaticamente**
   - Nome, código de referência, classificações
   - Mostra status "✅ Dados preenchidos da ANAC"

4. **Usuário pode editar campos se necessário**
   - Todos os campos permanecem editáveis
   - Pode ajustar dados calculados se souber valores mais precisos

5. **Usuário completa campos restantes**
   - Tipo de aeroporto
   - Operações (internacionais, carga, manutenção)
   - Número de pistas
   - Peso máximo de aeronaves

## ⚠️ Limitações e Considerações

### 1. **Aeroportos Não Encontrados**
- Se o aeroporto não estiver na lista ANAC, mostra erro
- Usuário pode continuar cadastrando manualmente

### 2. **Dados Parciais**
- Alguns aeroportos podem não ter todos os campos na ANAC
- Sistema preenche o que estiver disponível
- Usuário completa o restante manualmente

### 3. **Cálculos Estimados**
- `usage_class` e `avsec_classification` são estimados baseados na categoria
- Se o usuário souber valores mais precisos, pode editar manualmente

### 4. **Cache**
- Cada busca faz requisição à ANAC
- Considerar implementar cache local para melhorar performance

## 🚀 Melhorias Futuras

### Curto Prazo:
1. ✅ Implementar cache de dados ANAC (evitar múltiplas requisições)
2. ✅ Adicionar indicador visual de quais campos vieram da ANAC
3. ✅ Permitir sincronização de aeroportos já cadastrados

### Médio Prazo:
1. ✅ Autocomplete de códigos ICAO enquanto usuário digita
2. ✅ Validação em tempo real contra lista ANAC
3. ✅ Sugestões de correção se código estiver incorreto

### Longo Prazo:
1. ✅ Sincronização automática periódica
2. ✅ Notificações sobre mudanças na ANAC
3. ✅ Histórico de alterações de dados

## 📝 Notas Técnicas

### Endpoint Backend
- **URL:** `/api/airports/lookup/{icao_code}`
- **Método:** GET
- **Validação:** Código ICAO deve ter 4 letras
- **Erros:**
  - 400: Código inválido
  - 404: Aeroporto não encontrado
  - 503: Erro ao baixar dados da ANAC

### Prioridade de Busca (ANAC como fonte preferida)
1. **ANAC ao vivo** – download direto do site oficial
2. **Cache ANAC** – dados salvos em `data/anac_airports_cache.json` (7 dias)
3. **Banco local** – cadastro existente (se ANAC indisponível)

O cache é atualizado automaticamente quando a ANAC responde. O link "Atualizar cache ANAC" e o endpoint `POST /api/airports/sync/anac/refresh-cache` permitem atualização manual.

### Funções JavaScript
- `updateLookupButton()`: Habilita/desabilita botão baseado no código
- `lookupAirportFromANAC()`: Busca e preenche dados automaticamente
- `refreshAnacCache()`: Atualiza o cache ANAC manualmente

### Integração com Cálculos Existentes
- Após preencher `usage_class`, chama `calculateANACClassifications()`
- Mantém consistência com lógica de cálculo existente
