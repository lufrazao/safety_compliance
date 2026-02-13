# Análise: Preenchimento Automático de Dados de Aeroporto

## 📋 Campos que Podem Ser Preenchidos Automaticamente

### 1. **Dados Diretos da ANAC (via código ICAO)**

Quando o usuário informa o código ICAO, podemos buscar na lista oficial da ANAC:

| Campo | Fonte ANAC | Tipo | Observações |
|-------|------------|------|-------------|
| **Nome oficial** | `Nome do Aeródromo` | String | Nome completo e oficial |
| **Código ICAO** | `Código ICAO` | String | Já digitado pelo usuário (validação) |
| **Código IATA** | `Código IATA` | String | 3 letras (ex: GRU, GIG) |
| **Cidade** | `Cidade` / `Município` | String | Nome da cidade |
| **Estado (UF)** | `Estado` / `UF` | String | 2 letras (ex: SP, RJ) |
| **Latitude** | `Latitude` | Float | Coordenada geográfica |
| **Longitude** | `Longitude` | Float | Coordenada geográfica |
| **Status Operacional** | `Status` / `Situação` | String | Status oficial (ex: "Operacional") |
| **Código de Referência** | `Código de Referência` | String | Se disponível (ex: 3C, 4E) |

### 2. **Campos Calculados/Inferidos**

Baseados nos dados da ANAC ou em lógica de negócio:

| Campo | Fonte/Calculo | Lógica |
|-------|--------------|--------|
| **Usage Class (Classe por Uso)** | Cálculo baseado em passageiros anuais | Se ANAC fornecer passageiros: < 200k = I, 200k-1M = II, 1M-5M = III, > 5M = IV |
| **AVSEC Classification** | Cálculo baseado em passageiros anuais | < 600k = AP-1, 600k-5M = AP-2, > 5M = AP-3 |
| **Aircraft Size Category** | Inferido de `reference_code` ou `max_aircraft_weight` | Se reference_code: último caractere (C, D, E) → categoria. Se peso: < 5.7t = A/B, 5.7-136t = C, > 136t = D |
| **Size** | Calculado de `usage_class` | PRIVADO/I = SMALL, II = MEDIUM, III = LARGE, IV = INTERNATIONAL |
| **Annual Passengers** | Estimativa baseada em `usage_class` | I = 100k, II = 600k, III = 3M, IV = 10M |

### 3. **Campos que Requerem Input do Usuário**

Estes campos não podem ser preenchidos automaticamente:

| Campo | Motivo |
|-------|--------|
| **Airport Type** | Depende de operações específicas (comercial, geral, militar, misto) |
| **Has International Operations** | Informação operacional específica |
| **Has Cargo Operations** | Informação operacional específica |
| **Has Maintenance Facility** | Informação operacional específica |
| **Number of Runways** | Pode variar e requer verificação |
| **Max Aircraft Weight** | Depende de operações específicas do aeroporto |

## 🔄 Fluxo de Preenchimento Automático Proposto

### Opção 1: Busca Automática ao Digitar ICAO (Recomendado)

```
1. Usuário digita código ICAO no campo "Código"
   └─> Sistema aguarda 1 segundo após parar de digitar (debounce)

2. Sistema valida formato (4 letras)
   └─> Se válido, mostra botão "🔍 Buscar da ANAC"

3. Usuário clica "Buscar da ANAC"
   └─> Sistema faz requisição: GET /api/airports/lookup/{icao_code}

4. Sistema recebe dados da ANAC
   └─> Preenche campos automaticamente
   └─> Mostra indicador "✅ Dados da ANAC"
   └─> Permite edição manual se necessário

5. Campos calculados são preenchidos automaticamente
   └─> Usage Class, AVSEC, Size, etc.
```

### Opção 2: Busca Automática com Autocomplete

```
1. Usuário digita código ICAO
   └─> Sistema mostra sugestões de aeroportos conhecidos

2. Usuário seleciona aeroporto
   └─> Sistema preenche todos os campos automaticamente
```

## 🎯 Implementação Técnica

### Backend: Novo Endpoint

```python
@app.get("/api/airports/lookup/{icao_code}")
async def lookup_airport_from_anac(
    icao_code: str,
    db: Session = Depends(get_db)
):
    """
    Busca dados de um aeroporto na lista oficial da ANAC.
    
    Retorna dados que podem ser usados para preencher o formulário.
    """
    sync_service = ANACSyncService(db=db)
    
    # Buscar na lista ANAC
    anac_data = sync_service.download_anac_data()
    
    # Encontrar aeroporto pelo código ICAO
    airport_data = None
    for data in anac_data:
        if data.get('code', '').upper() == icao_code.upper():
            airport_data = data
            break
    
    if not airport_data:
        raise HTTPException(
            status_code=404,
            detail=f"Aeroporto {icao_code} não encontrado na lista ANAC"
        )
    
    # Calcular campos derivados
    calculated_fields = calculate_derived_fields(airport_data)
    
    return {
        **airport_data,
        **calculated_fields,
        "source": "anac",
        "last_updated": datetime.utcnow().isoformat()
    }
```

### Frontend: Botão de Busca

```javascript
// Adicionar botão ao lado do campo "Código"
<input type="text" id="code" ... />
<button type="button" onclick="lookupFromANAC()">
    🔍 Buscar da ANAC
</button>

async function lookupFromANAC() {
    const code = document.getElementById('code').value.trim().toUpperCase();
    
    if (code.length !== 4) {
        showToast('Código ICAO deve ter 4 letras', 'error');
        return;
    }
    
    try {
        showLoading('Buscando dados da ANAC...');
        const response = await fetch(`${API_BASE}/airports/lookup/${code}`);
        
        if (!response.ok) {
            throw new Error('Aeroporto não encontrado na ANAC');
        }
        
        const data = await response.json();
        
        // Preencher campos automaticamente
        document.getElementById('name').value = data.name || '';
        document.getElementById('codigo_iata').value = data.iata_code || '';
        document.getElementById('cidade').value = data.city || '';
        document.getElementById('estado').value = data.state || '';
        document.getElementById('latitude').value = data.latitude || '';
        document.getElementById('longitude').value = data.longitude || '';
        document.getElementById('reference_code').value = data.reference_code || '';
        
        // Preencher campos calculados
        if (data.usage_class) {
            document.getElementById('usage_class').value = data.usage_class;
            // Trigger cálculo automático de outros campos
            calculateANACClassifications();
        }
        
        showToast('✅ Dados preenchidos da ANAC', 'success');
        
    } catch (error) {
        showToast(`Erro: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}
```

## 📊 Benefícios

### Para o Usuário
- ✅ **Redução de erros**: Dados oficiais garantem precisão
- ✅ **Economia de tempo**: Preenchimento automático
- ✅ **Validação**: Código ICAO validado contra lista oficial
- ✅ **Dados atualizados**: Sempre sincronizado com ANAC

### Para o Sistema
- ✅ **Consistência**: Dados sempre alinhados com fonte oficial
- ✅ **Rastreabilidade**: Saber origem dos dados (manual vs. ANAC)
- ✅ **Confiabilidade**: Menos erros de digitação

## ⚠️ Considerações

### 1. **Aeroportos Não Encontrados**
- Se aeroporto não estiver na lista ANAC, permitir cadastro manual
- Mostrar aviso: "Aeroporto não encontrado na ANAC. Você pode cadastrar manualmente."

### 2. **Dados Parciais**
- Alguns aeroportos podem não ter todos os campos na ANAC
- Preencher o que estiver disponível e deixar o resto para o usuário

### 3. **Edição Manual**
- Sempre permitir edição manual após preenchimento automático
- Indicar visualmente quais campos vieram da ANAC

### 4. **Cache**
- Cachear dados da ANAC para evitar múltiplas requisições
- Atualizar cache periodicamente (a cada 30-40 dias)

## 🚀 Próximos Passos

1. ✅ Criar endpoint `/api/airports/lookup/{icao_code}`
2. ✅ Adicionar botão "Buscar da ANAC" no frontend
3. ✅ Implementar função de preenchimento automático
4. ✅ Adicionar indicadores visuais de origem dos dados
5. ✅ Implementar cache de dados ANAC
