# Análise: Integração com AISWEB/DECEA e ANAC para Melhoria do Sistema

**Data da Análise:** 31 de Janeiro de 2025  
**Fonte:** AISWEB/DECEA (https://aisweb.decea.mil.br/eaip/) e ANAC (Lista de Aeródromos Públicos)

---

## 📋 Resumo Executivo

O sistema pode ser significativamente melhorado através da integração com fontes oficiais de dados:
- **ANAC**: Lista oficial de aeródromos públicos (CSV/JSON)
- **AISWEB/DECEA**: Informações aeronáuticas operacionais (EAIP - Electronic Aeronautical Information Publication)

---

## 🎯 Oportunidades de Melhoria Identificadas

### 1. **Fonte Única de Verdade para Cadastro de Aeroportos**

#### Situação Atual
- Sistema permite cadastro manual de aeroportos
- Categoria e código de referência são inseridos manualmente
- Não há validação contra dados oficiais

#### Oportunidade
**Integrar com a Lista de Aeródromos Públicos da ANAC (V2)**

**Fonte:** [Lista de aeródromos públicos V2](https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/lista-de-aerodromos-publicos-v2)

**Benefícios:**
- ✅ Preenchimento automático de dados cadastrais
- ✅ Validação de códigos ICAO/IATA
- ✅ Sincronização de categorias e códigos de referência oficiais
- ✅ Redução de erros de digitação
- ✅ Atualização automática quando ANAC atualiza os dados (~40 dias)

**Campos que podem ser preenchidos automaticamente:**
- Nome oficial do aeródromo
- Código ICAO
- Código IATA (se disponível)
- Categoria do aeródromo
- Código de referência
- Localização (cidade, estado, coordenadas)
- Tipo de aeródromo
- Status operacional

---

### 2. **Informações Operacionais do AISWEB/DECEA**

#### Situação Atual
- Sistema foca em compliance regulatório
- Não integra informações operacionais em tempo real

#### Oportunidade
**Integrar dados do EAIP (Electronic Aeronautical Information Publication)**

**Fonte:** AISWEB/DECEA - https://aisweb.decea.mil.br/eaip/

**Informações úteis disponíveis:**
- Procedimentos de pouso e decolagem
- Restrições operacionais
- Horários de operação
- Frequências de comunicação
- NOTAMs (Notices to Airmen)
- Condições meteorológicas específicas
- Capacidades operacionais

**Benefícios:**
- ✅ Alertas sobre restrições que afetam compliance
- ✅ Validação de procedimentos operacionais
- ✅ Integração com requisitos de segurança operacional
- ✅ Monitoramento de mudanças que impactam conformidade

---

### 3. **Validação e Reconciliação de Dados**

#### Situação Atual
- Dados inseridos manualmente podem divergir dos oficiais
- Não há mecanismo de validação contra fontes oficiais

#### Oportunidade
**Sistema de Validação e Reconciliação**

**Implementar:**
1. **Validação em tempo real:**
   - Ao cadastrar/editar aeroporto, validar código ICAO contra lista ANAC
   - Sugerir correções quando houver divergências
   - Alertar sobre dados desatualizados

2. **Reconciliação periódica:**
   - Sincronização automática a cada 30-40 dias
   - Detecção de mudanças (categoria, status, etc.)
   - Notificações sobre alterações que requerem atenção

3. **Auditoria de origem:**
   - Rastrear origem dos dados (manual vs. ANAC)
   - Timestamp da última sincronização
   - Histórico de alterações

---

## 🔧 Implementação Técnica Proposta

### Fase 1: Integração com Lista ANAC (Prioridade Alta)

#### 1.1. Modelo de Dados

**Adicionar campos ao modelo `Airport`:**

```python
# Campos de sincronização
data_sincronizacao_anac = Column(DateTime, nullable=True)  # Última sincronização
origem_dados = Column(String(20), default="manual")  # "manual" ou "anac"
versao_dados_anac = Column(String(50), nullable=True)  # Versão do dataset ANAC

# Campos adicionais da ANAC
codigo_iata = Column(String(3), nullable=True)  # Código IATA (3 letras)
latitude = Column(Float, nullable=True)  # Coordenadas geográficas
longitude = Column(Float, nullable=True)
cidade = Column(String(100), nullable=True)
estado = Column(String(2), nullable=True)  # UF
status_operacional = Column(String(50), nullable=True)  # Status oficial ANAC
```

#### 1.2. Script de Ingestão

**Criar:** `app/services/anac_sync.py`

**Funcionalidades:**
- Download do CSV/JSON da ANAC
- Parsing e normalização dos dados
- Mapeamento de campos ANAC → modelo do sistema
- Detecção de mudanças
- Atualização/criação de registros
- Logging de alterações

**Estrutura proposta:**

```python
class ANACSyncService:
    def download_anac_data(self) -> List[Dict]:
        """Baixa e parseia dados da ANAC"""
        pass
    
    def sync_airports(self, anac_data: List[Dict]) -> SyncResult:
        """Sincroniza aeroportos com dados ANAC"""
        pass
    
    def detect_changes(self, airport: Airport, anac_data: Dict) -> List[Change]:
        """Detecta mudanças entre dados locais e ANAC"""
        pass
    
    def reconcile_airport(self, airport: Airport, anac_data: Dict) -> Airport:
        """Reconcilia dados locais com dados ANAC"""
        pass
```

#### 1.3. Endpoint de Sincronização

**Criar:** `POST /api/airports/sync/anac`

**Funcionalidades:**
- Sincronização manual sob demanda
- Retorna relatório de alterações
- Permite revisão antes de aplicar mudanças

#### 1.4. Validação no Frontend

**Melhorias no formulário:**
- Autocomplete de códigos ICAO baseado em lista ANAC
- Validação em tempo real contra dados ANAC
- Indicador visual de dados sincronizados vs. manuais
- Botão "Sincronizar com ANAC" para atualizar dados

---

### Fase 2: Integração com AISWEB/DECEA (Prioridade Média)

#### 2.1. Serviço de Consulta AISWEB

**Criar:** `app/services/aisweb_service.py`

**Funcionalidades:**
- Consulta de informações do EAIP por código ICAO
- Parsing de dados operacionais
- Cache de resultados
- Alertas sobre NOTAMs relevantes

#### 2.2. Dashboard de Informações Operacionais

**Adicionar seção no sistema:**
- Informações operacionais do aeroporto
- NOTAMs ativos
- Restrições operacionais
- Procedimentos em vigor

---

### Fase 3: Sistema de Notificações (Prioridade Média)

#### 3.1. Alertas Automáticos

**Implementar notificações para:**
- Mudanças de categoria/código de referência na ANAC
- NOTAMs que afetam compliance
- Restrições operacionais que impactam normas
- Dados desatualizados (última sync > 60 dias)

---

## 📊 Mapeamento de Campos ANAC → Sistema

### Campos Diretos (Mapeamento 1:1)

| Campo ANAC | Campo Sistema | Tipo | Observações |
|------------|---------------|------|-------------|
| Nome do Aeródromo | `name` | String | Usar nome oficial |
| Código ICAO | `code` | String | Validar formato (4 letras) |
| Código IATA | `codigo_iata` | String | Novo campo |
| Categoria | `category` | Enum | Validar contra enum existente |
| Código de Referência | `reference_code` | String | Validar formato |
| Latitude | `latitude` | Float | Novo campo |
| Longitude | `longitude` | Float | Novo campo |
| Cidade | `cidade` | String | Novo campo |
| Estado (UF) | `estado` | String | Novo campo |
| Status | `status_operacional` | String | Novo campo |

### Campos Calculados/Derivados

| Campo ANAC | Campo Sistema | Lógica |
|------------|---------------|--------|
| Passageiros Anuais | `annual_passengers` | Pode ser inferido da categoria |
| Tamanho | `size` | Mapear categoria → size |
| Tipo | `airport_type` | Inferir de características operacionais |

---

## 🔄 Fluxo de Sincronização Proposto

### Sincronização Automática (Recomendado)

```
1. Agendamento (cron job / scheduler)
   └─> Executar a cada 30-40 dias

2. Download de dados ANAC
   └─> Baixar CSV/JSON da URL oficial

3. Parsing e normalização
   └─> Converter para formato interno

4. Detecção de mudanças
   └─> Comparar com dados locais

5. Aplicação de mudanças
   └─> Atualizar/criar registros
   └─> Registrar histórico

6. Notificações
   └─> Alertar sobre mudanças significativas
```

### Sincronização Manual

```
1. Usuário clica "Sincronizar com ANAC"
   └─> Endpoint: POST /api/airports/sync/anac

2. Sistema executa sync
   └─> Retorna relatório de alterações

3. Usuário revisa mudanças
   └─> Interface mostra diff

4. Usuário aprova/rejeita
   └─> Aplicar mudanças ou manter dados locais
```

---

## ⚠️ Considerações e Desafios

### 1. **Divergências de Dados**
- **Problema:** Dados locais podem divergir dos oficiais
- **Solução:** Sistema de reconciliação com opção de manter dados locais quando justificado
- **Auditoria:** Registrar todas as divergências e decisões

### 2. **Frequência de Atualização**
- **Problema:** ANAC atualiza ~40 dias, mas pode haver mudanças urgentes
- **Solução:** Sincronização automática + opção manual sob demanda
- **Monitoramento:** Alertar quando dados estão desatualizados

### 3. **Formato dos Dados**
- **Problema:** Formato CSV/JSON pode mudar
- **Solução:** Versionamento de parsers, validação de schema
- **Fallback:** Tratamento de erros e notificações

### 4. **Performance**
- **Problema:** Sincronização pode ser lenta com muitos aeroportos
- **Solução:** Processamento assíncrono, cache, otimização de queries

---

## 📈 Benefícios Esperados

### Para Usuários
- ✅ **Redução de erros:** Menos digitação manual
- ✅ **Dados atualizados:** Sincronização automática
- ✅ **Validação:** Códigos e categorias sempre corretos
- ✅ **Eficiência:** Preenchimento automático de formulários

### Para o Sistema
- ✅ **Confiabilidade:** Dados alinhados com fonte oficial
- ✅ **Rastreabilidade:** Histórico de alterações
- ✅ **Escalabilidade:** Suporte a muitos aeroportos
- ✅ **Manutenibilidade:** Menos dados inconsistentes

### Para Compliance
- ✅ **Precisão:** Categorias e códigos oficiais garantem aplicabilidade correta de normas
- ✅ **Atualização:** Mudanças de categoria são detectadas automaticamente
- ✅ **Auditoria:** Rastreamento de origem dos dados

---

## 🚀 Próximos Passos Recomendados

### Curto Prazo (1-2 semanas)
1. ✅ Analisar estrutura do CSV/JSON da ANAC V2
2. ✅ Criar mapeamento detalhado de campos
3. ✅ Implementar script de ingestão básico
4. ✅ Testar com dados reais

### Médio Prazo (1 mês)
1. ✅ Implementar sincronização automática
2. ✅ Adicionar campos de sincronização ao modelo
3. ✅ Criar interface de reconciliação
4. ✅ Implementar validação no frontend

### Longo Prazo (2-3 meses)
1. ✅ Integração com AISWEB/DECEA
2. ✅ Sistema de notificações
3. ✅ Dashboard de informações operacionais
4. ✅ Relatórios de sincronização

---

## 📚 Referências

- **ANAC - Lista de Aeródromos Públicos V2:** https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/lista-de-aerodromos-publicos-v2
- **ANAC - Metadados:** https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/lista-de-aerodromos-publicos/2-lista-de-aerodromos-publicos
- **AISWEB/DECEA:** https://aisweb.decea.mil.br/eaip/
- **Contato Técnico ANAC:** cadastro.aeroportuario@anac.gov.br

---

## 📝 Notas Técnicas

### Formato de Dados ANAC
- **Formato:** CSV/JSON
- **Periodicidade:** ~40 dias
- **Encoding:** UTF-8
- **Delimitador CSV:** Ponto e vírgula (;)

### Requisitos de Implementação
- **Bibliotecas:** `requests`, `pandas` (para CSV), `json` (para JSON)
- **Agendamento:** `APScheduler` ou `celery` (para sync automático)
- **Cache:** Redis ou memória (para dados AISWEB)
- **Logging:** Registrar todas as operações de sync

---

**Documento criado em:** 31/01/2025  
**Última atualização:** 31/01/2025  
**Status:** Proposta de implementação
