# Correção: Normas RBAC-153 para Aeroportos General Aviation

## 🔍 Problema Identificado

A aba "Áreas SESCINC" estava vazia para o aeroporto SBRJ (Santos Dummond) porque:

1. **Aeroporto classificado como `general_aviation`**
   - O aeroporto SBRJ está cadastrado como `AirportType.GENERAL_AVIATION`

2. **Normas RBAC-153 requeriam apenas `commercial` ou `mixed`**
   - Todas as 14 normas RBAC-153 tinham `applies_to_types: ["commercial", "mixed"]`
   - Não incluíam `general_aviation`

3. **Resultado: Nenhuma norma RBAC-153 aplicável**
   - O sistema retornava 34 registros (todos RBAC-154)
   - 0 registros RBAC-153 processados

## ✅ Solução Implementada

### Atualização das Normas RBAC-153

Todas as 14 normas RBAC-153 foram atualizadas para incluir `general_aviation` nos tipos aplicáveis:

**Antes:**
```json
"applies_to_types": ["commercial", "mixed"]
```

**Depois:**
```json
"applies_to_types": ["commercial", "mixed", "general_aviation"]
```

### Normas Atualizadas

1. ✅ RBAC-153-01: Determinação da CAT
2. ✅ RBAC-153-02: Operações Compatíveis com a CAT
3. ✅ RBAC-153-03: Agentes Extintores
4. ✅ RBAC-153-04: Carro Contraincêndio de Aeródromo (CCI)
5. ✅ RBAC-153-05: Veículos de Apoio
6. ✅ RBAC-153-06: Equipe de Serviço do SESCINC
7. ✅ RBAC-153-07: Tempo-Resposta do SESCINC
8. ✅ RBAC-153-08: Capacitação de Recursos Humanos
9. ✅ RBAC-153-09: Equipamentos de Uso
10. ✅ RBAC-153-10: Programa de Treinamento Recorrente
11. ✅ RBAC-153-11: Plano Contraincêndio de Aeródromo (PCINC)
12. ✅ RBAC-153-12: Infraestrutura da Seção Contraincêndio (SCI)
13. ✅ RBAC-153-13: Posto Avançado de Contraincêndio (PACI)
14. ✅ RBAC-153-14: Informações ao Órgão Regulador

## 📋 Próximos Passos

### Para o Usuário:

1. **Executar "Verificar Conformidade" novamente**
   - Navegue para a aba "Verificar Conformidade"
   - Selecione o aeroporto SBRJ (Santos Dummond)
   - Clique em "Verificar Conformidade"
   - Isso criará os registros RBAC-153 para este aeroporto

2. **Verificar Áreas SESCINC**
   - Após verificar conformidade, navegue para a aba "Áreas SESCINC"
   - As áreas funcionais devem aparecer corretamente

### Para o Sistema:

- As normas RBAC-153 agora se aplicam a:
  - ✅ Aeroportos comerciais
  - ✅ Aeroportos mistos
  - ✅ Aeroportos de aviação geral (general_aviation)

## 🔄 Impacto

- **Aeroportos existentes:** Precisam executar "Verificar Conformidade" novamente para criar registros RBAC-153
- **Novos aeroportos:** Automaticamente terão normas RBAC-153 aplicadas se forem `general_aviation`, `commercial` ou `mixed`

## 📝 Nota Técnica

A decisão de incluir `general_aviation` foi baseada em:
- Documentação SESCINC indica aplicabilidade a "todos os aeroportos comerciais"
- Aeroportos de aviação geral também podem ter operações comerciais
- Melhor cobertura de conformidade para todos os tipos de aeroportos
