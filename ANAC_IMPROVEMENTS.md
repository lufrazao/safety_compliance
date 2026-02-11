# Melhorias do Sistema Baseadas nas Diretrizes ANAC

## Resumo das Alterações

Este documento descreve as melhorias implementadas no sistema de conformidade aeroportuária baseadas na análise dos checklists oficiais da ANAC (DOCS REA e TOPS REA).

## 1. Sistema de Classificação D/C/B/A

### Implementação
- Adicionado enum `RequirementClassification` com valores D, C, B, A
- Integrado ao modelo `Regulation` para classificar cada norma

### Significado das Classificações
- **D (Essencial)**: Requisitos essenciais - requer 85% mínimo de conformidade para concessão do ACOP
- **C (Complementar)**: Requisitos complementares - contam pontos para upgrade no ACOP
- **B (Recomendada)**: Práticas recomendadas - extrapolam mínimos regulamentares
- **A (Melhor Prática)**: Melhores práticas - estado da arte, controles de performance

## 2. Sistema de Pontuação Ponderada

### Implementação
- Campo `weight` (peso) adicionado ao modelo `Regulation`
- Cálculo de pontuação ponderada baseado no peso de cada item
- Separação de pontuações por classificação (D, C, B, A)

### Cálculo de Conformidade
- **Itens D**: Calcula percentual de conformidade ponderado
- **Verificação de 85%**: Sistema verifica automaticamente se itens D atingem 85% mínimo
- **Pontuação Geral**: Calcula pontuação geral ponderada considerando todos os itens

## 3. Avaliação em Duas Etapas (DOCS e TOPS)

### Implementação
- Enum `EvaluationType` com valores: DOCS, TOPS, BOTH
- Campo `evaluation_type` no modelo `Regulation`
- Campos `docs_score` e `tops_score` no modelo `ComplianceRecord`

### Tipos de Avaliação
- **DOCS**: Verificação documental à distância (formulários, laudos, relatórios)
- **TOPS**: Verificação operacional no local (testes práticos)
- **BOTH**: Requer ambas as verificações

## 4. Referências Normativas ANAC

### Implementação
- Campo `anac_reference` para armazenar referências normativas (ex: 153.323(e))
- Campo `expected_performance` para descrição do desempenho esperado/verificação

## 5. Interface do Usuário

### Melhorias Visuais
- **Painel de Pontuação ANAC**: Exibe pontuações por classificação (D, C, B, A)
- **Badges de Classificação**: Mostra classificação de cada norma com cores distintas
- **Indicador de Peso**: Exibe o peso de cada item
- **Tipo de Avaliação**: Indica se é DOCS, TOPS ou ambos
- **Referência ANAC**: Mostra referência normativa quando disponível

### Cores e Indicadores
- **D (Essencial)**: Vermelho - indica importância crítica
- **C (Complementar)**: Azul
- **B (Recomendada)**: Laranja
- **A (Melhor Prática)**: Roxo

## 6. Cálculo Automático de Conformidade

### Lógica Implementada
```python
def _calculate_anac_scores(records, regulations):
    # Separa itens por classificação (D, C, B, A)
    # Calcula peso total e peso conforme por classificação
    # Verifica se itens D atingem 85% mínimo
    # Calcula pontuação geral ponderada
    # Retorna scores detalhados
```

### Recomendações Automáticas
- Alerta quando itens D estão abaixo de 85%
- Sugere foco em itens complementares (C) e recomendadas (B) para melhorar ACOP
- Fornece feedback específico baseado nas pontuações

## 7. Estrutura de Dados

### Novos Campos no Modelo `Regulation`
- `requirement_classification`: D, C, B, ou A
- `evaluation_type`: DOCS, TOPS, ou BOTH
- `weight`: Peso do item (1-10 tipicamente)
- `anac_reference`: Referência normativa
- `expected_performance`: Desempenho esperado/verificação

### Novos Campos no Modelo `ComplianceRecord`
- `docs_score`: Pontuação DOCS (0-100)
- `tops_score`: Pontuação TOPS (0-100)
- `weighted_score`: Pontuação ponderada geral
- `is_essential_compliant`: Boolean indicando se itens D atingem 85%

## 8. Próximos Passos Recomendados

1. **Importar Dados dos Checklists**: Criar script para importar os 82 itens DOCS e 157 itens TOPS dos arquivos Excel
2. **Mapear Classificações**: Associar classificações D/C/B/A aos regulamentos existentes
3. **Definir Pesos**: Atribuir pesos apropriados baseados nos checklists
4. **Configurar Avaliações**: Definir se cada norma requer DOCS, TOPS ou ambos
5. **Testar Cálculos**: Validar cálculos de pontuação com dados reais

## 9. Arquivos Modificados

- `app/models.py`: Adicionados enums e campos novos
- `app/schemas.py`: Atualizados schemas Pydantic
- `app/compliance_engine.py`: Implementada lógica de cálculo ANAC
- `app/main.py`: Atualizados endpoints para incluir novos campos
- `static/index.html`: Interface atualizada com informações ANAC

## 10. Notas Importantes

⚠️ **Atenção**: O banco de dados precisa ser recriado para incluir os novos campos. Execute:
```bash
python -m app.seed_data
```

O sistema agora está alinhado com as diretrizes oficiais da ANAC para avaliação de conformidade safety dos aeroportos certificados.
