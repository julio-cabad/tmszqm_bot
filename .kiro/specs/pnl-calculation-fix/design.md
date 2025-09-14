# Design Document

## Overview

El diseño se enfoca en corregir los cálculos de PnL en el sistema Spartan Trading System, específicamente en el PnLSimulator y OrderManager. El problema principal radica en inconsistencias entre los cálculos de quantity, gross PnL, y real PnL que no reflejan correctamente posiciones de $100.

## Architecture

### Current Architecture Issues
- **OrderManager**: Calcula quantity correctamente para posiciones de $100
- **PnLSimulator**: Recibe los valores pero los cálculos de PnL no son consistentes
- **StrategyMonitor**: Pasa correctamente los valores entre componentes

### Proposed Architecture
- Mantener la arquitectura actual pero corregir los algoritmos de cálculo
- Agregar validación de consistencia en los cálculos
- Mejorar el logging para debugging

## Components and Interfaces

### 1. OrderManager (Minor Updates)
**Current Interface:**
```python
def generate_order_suggestion(symbol, signal_type, current_price, tm_value, timeframe) -> OrderSuggestion
```

**Updates Needed:**
- Validar que `position_value = quantity * entry_price ≈ $100`
- Agregar logging detallado de cálculos

### 2. PnLSimulator (Major Updates)
**Current Interface:**
```python
def calculate_pnl(current_price: float) -> float
def calculate_real_pnl(current_price: float, exit_commission: float) -> float
```

**Updates Needed:**
- Corregir fórmulas de cálculo de PnL
- Validar consistencia de cálculos
- Mejorar logging de debug

### 3. Position Class (Updates)
**Current Interface:**
```python
@dataclass
class Position:
    symbol: str
    side: PositionSide
    entry_price: float
    quantity: float
    # ... otros campos
```

**Updates Needed:**
- Agregar campo `invested_capital` para tracking preciso
- Validar que `invested_capital = entry_price * quantity`

## Data Models

### Enhanced Position Model
```python
@dataclass
class Position:
    symbol: str
    side: PositionSide
    entry_price: float
    quantity: float
    invested_capital: float  # NEW: Para tracking preciso
    stop_loss: float
    take_profit: float
    entry_time: datetime
    entry_commission: float
    
    def __post_init__(self):
        # Validar consistencia
        calculated_capital = self.entry_price * self.quantity
        if abs(calculated_capital - self.invested_capital) > 0.01:
            raise ValueError(f"Inconsistent capital calculation: {calculated_capital} vs {self.invested_capital}")
```

### PnL Calculation Formulas

#### For LONG Positions:
```python
gross_pnl = (current_price - entry_price) * quantity
real_pnl = gross_pnl - entry_commission - exit_commission
pnl_percentage = (real_pnl / invested_capital) * 100
```

#### For SHORT Positions:
```python
gross_pnl = (entry_price - current_price) * quantity
real_pnl = gross_pnl - entry_commission - exit_commission
pnl_percentage = (real_pnl / invested_capital) * 100
```

## Error Handling

### Validation Checks
1. **Position Opening Validation:**
   - Verificar que `quantity * entry_price ≈ 100.0` (±$0.01 tolerance)
   - Validar que quantity > 0
   - Confirmar que precios son válidos

2. **PnL Calculation Validation:**
   - Verificar que los cálculos son matemáticamente consistentes
   - Alertar si hay discrepancias mayores al 1%
   - Logear cálculos detallados para debugging

3. **Commission Validation:**
   - Verificar que las comisiones se calculan sobre valores correctos
   - Confirmar que las tasas de comisión son válidas

### Error Recovery
- Si se detectan inconsistencias, logear error detallado
- Continuar operación pero marcar posición para revisión
- Proporcionar información de debugging completa

## Testing Strategy

### Unit Tests
1. **Test Position Creation:**
   - Verificar cálculo correcto de quantity para $100
   - Validar que invested_capital es correcto
   - Confirmar cálculos de comisiones

2. **Test PnL Calculations:**
   - LONG positions con precios subiendo/bajando
   - SHORT positions con precios subiendo/bajando
   - Casos edge con precios muy pequeños/grandes

3. **Test Validation Logic:**
   - Casos donde las validaciones deben fallar
   - Recuperación de errores
   - Logging de debugging

### Integration Tests
1. **OrderManager → PnLSimulator Flow:**
   - Verificar que los valores se pasan correctamente
   - Confirmar que las posiciones se abren con $100 exactos
   - Validar cálculos end-to-end

2. **Real Market Data Tests:**
   - Usar datos reales de BTCUSDT, BNBUSDT, etc.
   - Verificar cálculos con diferentes rangos de precios
   - Confirmar consistencia a lo largo del tiempo

### Performance Tests
- Verificar que las validaciones no impacten significativamente el rendimiento
- Confirmar que el logging adicional es eficiente
- Medir tiempo de cálculos de PnL

## Implementation Notes

### Debugging Enhancements
```python
def calculate_pnl_with_debug(self, current_price: float) -> float:
    """Calculate PnL with detailed debugging information"""
    if self.side == PositionSide.LONG:
        price_diff = current_price - self.entry_price
        gross_pnl = price_diff * self.quantity
    else:
        price_diff = self.entry_price - current_price
        gross_pnl = price_diff * self.quantity
    
    # Detailed logging
    self.logger.debug(
        f"🔍 PnL Debug {self.symbol}: "
        f"Entry=${self.entry_price:.4f} | Current=${current_price:.4f} | "
        f"Qty={self.quantity:.6f} | PriceDiff=${price_diff:.4f} | "
        f"Gross=${gross_pnl:.4f} | Capital=${self.invested_capital:.2f}"
    )
    
    return gross_pnl
```

### Validation Framework
```python
def validate_position_consistency(self) -> bool:
    """Validate that position calculations are consistent"""
    calculated_capital = self.entry_price * self.quantity
    capital_diff = abs(calculated_capital - self.invested_capital)
    
    if capital_diff > 0.01:  # $0.01 tolerance
        self.logger.error(
            f"💀 Position inconsistency {self.symbol}: "
            f"Calculated=${calculated_capital:.4f} vs Expected=${self.invested_capital:.4f}"
        )
        return False
    
    return True
```