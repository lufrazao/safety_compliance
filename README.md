# Sistema de Conformidade ANAC - Aeroportos

Sistema de gestão de conformidade para aeroportos brasileiros, desenvolvido para ajudar equipes aeroportuárias a identificar normas, verificar conformidade e entender o que precisa ser feito para estar em conformidade com os regulamentos da ANAC (Agência Nacional de Aviação Civil).

## Características

- ✅ **Verificação Automática de Conformidade**: O sistema avalia automaticamente quais normas se aplicam a cada aeroporto com base em suas características (tamanho, tipo, operações, etc.)
- 📋 **Gestão de Normas**: Banco de dados com 55+ regulamentos ANAC (RBAC-153 e RBAC-154) organizados por categorias de segurança
- 🎯 **Recomendações Personalizadas**: Gera recomendações específicas baseadas no perfil do aeroporto e status de conformidade
- 📝 **Geração Automática de Itens de Ação**: O sistema gera automaticamente itens de ação detalhados para cada norma, ajudando as equipes a entender exatamente o que precisa ser feito para alcançar conformidade
- 📊 **Dashboard Visual**: Interface web intuitiva para visualizar status de conformidade
- 🔍 **Filtragem Inteligente**: Apenas normas aplicáveis são apresentadas, baseadas em variáveis do aeroporto

## Variáveis do Aeroporto

O sistema considera as seguintes variáveis para determinar quais normas se aplicam:

- **Tamanho**: Pequeno, Médio, Grande, Internacional
- **Tipo**: Comercial, Aviação Geral, Militar, Misto
- **Passageiros anuais**: Número de passageiros por ano
- **Operações internacionais**: Sim/Não
- **Operações de carga**: Sim/Não
- **Facilidades de manutenção**: Sim/Não
- **Número de pistas**
- **Peso máximo de aeronaves**

## Categorias de Segurança

O sistema organiza as normas em categorias:

1. **Segurança Operacional** (Operational Safety)
2. **Segurança contra Incêndio** (Fire Safety)
3. **Segurança da Aviação Civil** (Security/AVSEC)
4. **Infraestrutura** (Infrastructure)
5. **Resposta a Emergências** (Emergency Response)
6. **Meio Ambiente** (Environmental)
7. **Gerenciamento de Fauna** (Wildlife Management)
8. **Manutenção** (Maintenance)
9. **Certificação de Pessoal** (Personnel Certification)
10. **Serviços de Tráfego Aéreo** (Air Traffic Services)

## Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passos

1. Clone ou baixe este repositório

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Inicialize o banco de dados e carregue os dados iniciais:
```bash
python -m app.seed_data
```

4. Inicie o servidor:
```bash
python -m app.main
```

Ou usando uvicorn diretamente:
```bash
uvicorn app.main:app --reload
```

5. Acesse a interface web:
   - Abra `static/index.html` no seu navegador
   - Ou acesse a documentação da API em: http://localhost:8000/docs

## Uso

### Interface Web

1. Abra `static/index.html` no seu navegador
2. Selecione um aeroporto da lista
3. Clique em "Verificar Conformidade"
4. Visualize o status de conformidade, normas aplicáveis e recomendações

### API REST

A API fornece endpoints para:

- **Aeroportos**: CRUD de aeroportos
- **Normas**: CRUD de regulamentos
- **Conformidade**: Verificação e gestão de status de conformidade

#### Exemplos de uso da API:

**Listar aeroportos:**
```bash
curl http://localhost:8000/api/airports
```

**Verificar conformidade:**
```bash
curl -X POST http://localhost:8000/api/compliance/check \
  -H "Content-Type: application/json" \
  -d '{"airport_id": 1}'
```

**Listar normas:**
```bash
curl http://localhost:8000/api/regulations
```

## Estrutura do Projeto

```
safety_compliance/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicação FastAPI principal
│   ├── models.py            # Modelos de dados (SQLAlchemy)
│   ├── schemas.py           # Schemas Pydantic para validação
│   ├── database.py          # Configuração do banco de dados
│   ├── compliance_engine.py # Motor de verificação de conformidade
│   └── seed_data.py         # Script para popular dados iniciais
├── static/
│   └── index.html           # Interface web
├── requirements.txt         # Dependências Python
└── README.md               # Este arquivo
```

## Banco de Dados

O sistema usa SQLite por padrão (pode ser facilmente alterado para PostgreSQL). O banco de dados contém três tabelas principais:

- **airports**: Perfis de aeroportos com suas variáveis
- **regulations**: Normas e regulamentos ANAC (41+ normas incluídas)
- **compliance_records**: Registros de status de conformidade com itens de ação gerados automaticamente

### Normas Incluídas

O sistema vem pré-carregado com 55 normas ANAC cobrindo todas as categorias de segurança:

- **RBAC-153 (SESCINC)**: 14 regulamentações específicas para Serviço de Salvamento e Combate a Incêndio em Aeródromos Civis
- **RBAC-154**: 41 regulamentações gerais para aeroportos

- **Segurança Operacional**: SMS, investigação de incidentes, treinamento, gestão de riscos
- **Segurança contra Incêndio**: SCIR, equipamentos, detecção e alarme
- **Segurança da Aviação Civil**: AVSEC, controle de acesso, inspeções, proteção perimétrica
- **Infraestrutura**: Pistas, sinalização, iluminação, drenagem, operações de carga
- **Resposta a Emergências**: Planos de emergência, comunicação, equipamentos de resgate
- **Meio Ambiente**: Monitoramento de ruído, gestão de resíduos, controle de emissões
- **Gerenciamento de Fauna**: Inspeções, medidas preventivas
- **Manutenção**: Equipamentos, calibração, facilidades de manutenção aeronáutica
- **Certificação de Pessoal**: Supervisores, treinamento de segurança
- **Serviços de Tráfego Aéreo**: Torre de controle, navegação, comunicações

## Personalização

### Adicionar Novas Normas

Edite `app/seed_data.py` ou use a API para adicionar novas normas:

```python
POST /api/regulations
{
  "code": "RBAC-154-XX",
  "title": "Título da Norma",
  "description": "Descrição",
  "safety_category": "operational_safety",
  "applies_to_sizes": ["medium", "large"],
  "requirements": "Requisitos detalhados..."
}
```

### Adicionar Novos Aeroportos

Use a interface web ou a API:

```python
POST /api/airports
{
  "name": "Nome do Aeroporto",
  "code": "ICAO",
  "size": "medium",
  "airport_type": "commercial",
  ...
}
```

## Desenvolvimento Futuro

- [ ] Integração com APIs da ANAC para atualização automática de normas
- [ ] Sistema de notificações para prazos de conformidade
- [ ] Relatórios PDF exportáveis
- [ ] Histórico de auditorias
- [ ] Sistema de usuários e permissões
- [ ] Dashboard com gráficos e métricas
- [ ] API de webhooks para integrações

## Referências

- [ANAC - Agência Nacional de Aviação Civil](https://www.gov.br/anac/pt-br)
- [RBAC-154 - Regulamento Brasileiro da Aviação Civil para Aeroportos](https://www.gov.br/anac/pt-br/assuntos/regulados/aeroportos-e-aerodromos)

## Licença

Este projeto é fornecido como está, para fins educacionais e de demonstração.

## Contribuições

Contribuições são bem-vindas! Por favor, sinta-se à vontade para abrir issues ou pull requests.
