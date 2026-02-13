# Claude Documentation

Este arquivo contém documentação e notas sobre o projeto de conformidade aeroportuária ANAC.

## Visão Geral

Sistema de gestão de conformidade para aeroportos brasileiros, desenvolvido para apoiar coordenadores SESCINC na gestão de procedimentos e certificação de conformidade com os requisitos da ANAC.

## Estrutura do Projeto

- `app/` - Código da aplicação backend (FastAPI)
- `static/` - Frontend (HTML/CSS/JavaScript)
- `migrations/` - Scripts de migração do banco de dados
- `seed_data.py` - Dados iniciais (normas RBAC-153 e RBAC-154)

## Principais Funcionalidades

1. **Gestão de Aeroportos**: Cadastro e gerenciamento de aeroportos com classificações ANAC
2. **Verificação de Conformidade**: Verificação automática de conformidade com normas RBAC-153 e RBAC-154
3. **Gestão de Áreas Funcionais**: Organização por áreas funcionais do SESCINC
4. **Documentos**: Upload e gestão de documentos de evidência
5. **Relatórios**: Exportação de relatórios em Excel e PDF

## Classificações ANAC

### Por Uso (RBAC 153)
- Classe I: < 200 mil passageiros/ano
- Classe II: 200 mil - 1 milhão passageiros/ano
- Classe III: 1 milhão - 5 milhões passageiros/ano
- Classe IV: > 5 milhões passageiros/ano
- Privado: Uso restrito ao proprietário

### Classificação AVSEC
- AP-0: Aviação geral/táxi aéreo/fretamento
- AP-1: Comercial regular/charter, < 600 mil pass./ano
- AP-2: Comercial regular/charter, 600 mil - 5 milhões pass./ano
- AP-3: Comercial regular/charter, > 5 milhões pass./ano

### Categoria de Porte da Aeronave
- A/B: Aeronaves até 5.700 kg
- C: Aeronaves entre 5.700 kg e 136.000 kg
- D: Aeronaves acima de 136.000 kg

## Tecnologias

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Banco de Dados**: SQLite
- **Validação**: Pydantic

## Notas de Desenvolvimento

- O sistema utiliza enums do Python que são convertidos para strings antes da serialização JSON
- Campos de classificação de aeroporto são calculados automaticamente baseados em `usage_class`
- O sistema suporta campos customizados específicos para cada norma SESCINC
