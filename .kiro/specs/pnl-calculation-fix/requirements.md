# Requirements Document

## Introduction

El sistema de cálculo de PnL (Profit and Loss) del Spartan Trading System presenta inconsistencias en los cálculos de ganancias y pérdidas para posiciones de $100. Los cálculos actuales muestran valores incorrectos que no corresponden con los movimientos de precios reales, lo que afecta la precisión del simulador de trading y la confiabilidad de las métricas de rendimiento.

## Requirements

### Requirement 1

**User Story:** Como trader que usa el simulador de PnL, quiero que los cálculos de ganancias y pérdidas sean precisos y consistentes, para poder evaluar correctamente el rendimiento de mis estrategias.

#### Acceptance Criteria

1. WHEN una posición LONG de $100 se abre a un precio de entrada THEN la quantity debe calcularse como $100 / precio_entrada
2. WHEN el precio sube en una posición LONG THEN el Gross PnL debe ser positivo y proporcional al cambio de precio
3. WHEN el precio baja en una posición LONG THEN el Gross PnL debe ser negativo y proporcional al cambio de precio
4. WHEN el precio baja en una posición SHORT THEN el Gross PnL debe ser positivo y proporcional al cambio de precio
5. WHEN el precio sube en una posición SHORT THEN el Gross PnL debe ser negativo y proporcional al cambio de precio

### Requirement 2

**User Story:** Como desarrollador del sistema, quiero que las comisiones se calculen correctamente sobre el valor real de la posición, para que el Real PnL refleje las ganancias netas después de costos.

#### Acceptance Criteria

1. WHEN se abre una posición THEN la comisión de entrada debe calcularse como (precio_entrada × quantity × maker_fee)
2. WHEN se cierra una posición THEN la comisión de salida debe calcularse como (precio_salida × quantity × taker_fee)
3. WHEN se calcula el Real PnL THEN debe ser Gross PnL - comisión_entrada - comisión_salida
4. IF la posición está abierta THEN el Real PnL debe incluir la comisión de entrada y estimar la comisión de salida

### Requirement 3

**User Story:** Como usuario del sistema de monitoreo, quiero que los porcentajes de PnL se calculen correctamente basados en el capital invertido, para entender el rendimiento relativo de cada posición.

#### Acceptance Criteria

1. WHEN se calcula el porcentaje de PnL THEN debe basarse en el capital invertido ($100)
2. WHEN una posición tiene Real PnL de $1 THEN el porcentaje debe ser 1.0%
3. WHEN una posición tiene Real PnL de -$2 THEN el porcentaje debe ser -2.0%
4. WHEN se muestra el resumen de posiciones THEN los porcentajes deben ser consistentes con los valores absolutos

### Requirement 4

**User Story:** Como usuario del sistema, quiero que el logging de debug muestre información precisa de los cálculos, para poder verificar y diagnosticar problemas en el sistema.

#### Acceptance Criteria

1. WHEN se calculan los PnL THEN el log debe mostrar: Entry Price, Current Price, Quantity, Gross PnL, Real PnL
2. WHEN hay discrepancias en los cálculos THEN el sistema debe logear información detallada para debugging
3. WHEN se abren posiciones THEN el log debe confirmar que el valor de la posición es exactamente $100
4. IF los cálculos no cuadran THEN el sistema debe alertar sobre inconsistencias