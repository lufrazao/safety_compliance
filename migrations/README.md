# Migrations

Esta pasta contém scripts de migration para atualizar o esquema do banco de dados.

## Como executar uma migration

### Migration: Add custom_fields

Adiciona a coluna `custom_fields` à tabela `compliance_records` para suportar campos customizados SESCINC.

```bash
python migrations/add_custom_fields.py
```

### Migration: Add airport category and reference code

Adiciona as colunas `category` e `reference_code` à tabela `airports` para suportar categorias ANAC e códigos de referência.

```bash
python migrations/add_airport_category_and_reference_code.py
```

### Migration: Add ANAC synchronization fields

Adiciona campos para sincronização com dados oficiais da ANAC e informações adicionais (IATA, coordenadas, localização).

```bash
python migrations/add_anac_sync_fields.py
```

## Estrutura das Migrations

Cada migration:
- Verifica se a alteração já foi aplicada
- Executa apenas se necessário
- Fornece feedback claro sobre o progresso
- É idempotente (pode ser executada múltiplas vezes sem problemas)

## Backup Recomendado

Antes de executar migrations em produção:
1. Faça backup do banco de dados
2. Teste a migration em ambiente de desenvolvimento
3. Verifique se não há dados que serão afetados

## Migrations Disponíveis

### `add_custom_fields.py`
- **Data:** 2025-01-31
- **Descrição:** Adiciona coluna `custom_fields` (TEXT) à tabela `compliance_records`
- **Uso:** Armazena campos customizados SESCINC em formato JSON
- **Reversível:** Sim (pode ser removida manualmente se necessário)

### `add_airport_category_and_reference_code.py`
- **Data:** 2025-01-31
- **Descrição:** Adiciona colunas `category` e `reference_code` à tabela `airports`
- **Uso:** 
  - `category`: Categoria do aeroporto conforme classificação ANAC (1C-9C) baseada no número anual de passageiros
  - `reference_code`: Código de referência do aeroporto (ex: 3C, 4C, 5C)
- **Nota:** A coluna `annual_passengers` é mantida para compatibilidade
- **Reversível:** Sim (pode ser removida manualmente se necessário)

### `add_anac_sync_fields.py`
- **Data:** 2025-01-31
- **Descrição:** Adiciona campos de sincronização e dados adicionais da ANAC à tabela `airports`
- **Uso:** 
  - Campos de sincronização: `data_sincronizacao_anac`, `origem_dados`, `versao_dados_anac`
  - Dados adicionais: `codigo_iata`, `latitude`, `longitude`, `cidade`, `estado`, `status_operacional`
- **Reversível:** Sim (pode ser removida manualmente se necessário)

## Criando Novas Migrations

Ao criar uma nova migration:

1. Crie um arquivo Python na pasta `migrations/`
2. Use o padrão: `add_<feature>_<date>.py` ou `migrate_<version>.py`
3. Siga a estrutura do `add_custom_fields.py`:
   - Verificação de pré-condições
   - Execução da alteração
   - Verificação de sucesso
   - Mensagens claras ao usuário

4. Documente a migration neste README

## Notas Técnicas

- O sistema usa SQLite por padrão
- Migrations são compatíveis com SQLite, mas podem precisar de ajustes para PostgreSQL/MySQL
- Sempre teste migrations em ambiente de desenvolvimento primeiro
