"""
Spartan Trading System - Symbols Configuration
Centralized symbol management for all monitoring systems
"""

# Lista principal de símbolos para monitoreo
# Basada en tu signal_generator.py original
SPARTAN_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "DOTUSDT", 
    "BNBUSDT", "XRPUSDT", "AVAXUSDT", "LINKUSDT", "ATOMUSDT",
    "ALGOUSDT", "VETUSDT", "NEARUSDT", "SANDUSDT", "MANAUSDT",
    "CHZUSDT", "ENJUSDT", "GALAUSDT", "TIAUSDT", "DOGEUSDT",
    "SUIUSDT", "HBARUSDT"
]

# Símbolos adicionales disponibles (no activos por defecto)
ADDITIONAL_SYMBOLS = [
    "LTCUSDT", "BCHUSDT", "MATICUSDT", "FTMUSDT", "AXSUSDT"
]

# Todos los símbolos disponibles
ALL_SYMBOLS = SPARTAN_SYMBOLS + ADDITIONAL_SYMBOLS

def get_spartan_symbols():
    """Obtiene la lista principal de símbolos Spartan"""
    return SPARTAN_SYMBOLS.copy()

def get_all_symbols():
    """Obtiene todos los símbolos disponibles"""
    return ALL_SYMBOLS.copy()

def get_symbols_by_category(category: str = "spartan"):
    """
    Obtiene símbolos por categoría
    
    Args:
        category: "spartan", "additional", o "all"
    """
    if category == "spartan":
        return SPARTAN_SYMBOLS.copy()
    elif category == "additional":
        return ADDITIONAL_SYMBOLS.copy()
    elif category == "all":
        return ALL_SYMBOLS.copy()
    else:
        raise ValueError(f"Categoría desconocida: {category}")

def is_valid_symbol(symbol: str):
    """Verifica si un símbolo es válido"""
    return symbol in ALL_SYMBOLS