# Implementation Plan

- [x] 1. Fix PnL calculation formulas in Position class
  - Verify LONG formula: (current_price - entry_price) * quantity
  - Verify SHORT formula: (entry_price - current_price) * quantity  
  - Fix Real PnL calculation: gross_pnl - entry_commission - exit_commission
  - _Requirements: 1.2, 1.3, 1.4, 1.5, 2.3_

- [x] 2. Fix percentage calculation in get_open_positions_summary
  - Use invested capital ($100) as base for percentage calculation
  - Ensure pnl_pct = (real_pnl / 100.0) * 100
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 3. Add debug logging to identify the actual problem
  - Log quantity, entry_price, current_price, and position_value in PnL calculations
  - Show exact calculation steps in debug logs
  - _Requirements: 4.1, 4.2_