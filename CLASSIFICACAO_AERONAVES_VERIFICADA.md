# Verificação da Classificação de Aeronaves

## Classificação Implementada

A classificação de porte da aeronave foi implementada conforme as diretrizes da ANAC:

### Categorias por Porte da Aeronave (Avaliação de Pista)

- **A/B**: Aeronaves até 5.700 kg (MTOW - Maximum Take-Off Weight)
- **C**: Aeronaves entre 5.700 kg e 136.000 kg (MTOW)
- **D**: Aeronaves acima de 136.000 kg (MTOW)

## Observação sobre o Arquivo Excel

O arquivo `Caracteristicasfisicaseoperacionaisdeaeronavescomerciais.xlsx` contém o **Código de Referência de Aeronaves**, que é uma classificação diferente e mais detalhada:

### Código de Referência (do Excel)
- Combina número (comprimento de pista) + letra (porte)
- Exemplos: 1B, 2B, 3C, 4C, 4D, 4E, 4F
- Letras encontradas no Excel: B, C, D, E, F
- Faixas de peso no Excel:
  - **B**: 5.500 - 36.514 kg
  - **C**: 15.650 - 95.254 kg
  - **D**: 61.000 - 285.990 kg
  - **E**: 219.539 - 414.130 kg
  - **F**: 392.000 - 640.000 kg

### Diferença entre as Classificações

1. **Categoria de Porte da Aeronave (A/B, C, D)**: 
   - Classificação simplificada usada para avaliação de pista
   - Baseada apenas no MTOW
   - Usada no sistema para determinar requisitos de infraestrutura

2. **Código de Referência (1B, 2B, 3C, 4D, etc.)**:
   - Classificação mais detalhada da ICAO/ANAC
   - Considera comprimento de pista (número) + porte (letra)
   - Usado para especificações técnicas detalhadas de aeronaves

## Implementação no Sistema

O sistema usa a classificação simplificada (A/B, C, D) conforme solicitado, que é adequada para:
- Determinar requisitos de infraestrutura do aeródromo
- Avaliar conformidade com normas ANAC
- Classificar aeroportos por capacidade

O cálculo automático funciona assim:
- Se `max_aircraft_weight` ≤ 5.700 kg → **A/B**
- Se 5.700 kg < `max_aircraft_weight` ≤ 136.000 kg → **C**
- Se `max_aircraft_weight` > 136.000 kg → **D**

## Status

✅ **Classificação Correta**
- Implementada conforme diretrizes ANAC
- Cálculo automático funcionando
- Baseado em MTOW (peso máximo de decolagem)
