#!/usr/bin/env python3
"""
Simple Binance connection test
"""
import logging
from bnb.binance import RobotBinance
from config.settings import SYMBOLS

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_binance_connection():
    """Test basic Binance connection and price fetching"""
    print("🚀 Iniciando prueba de conexión a Binance...")
    
    try:
        # Crear instancia del robot con BTC
        robot = RobotBinance(pair="BTCUSDT", temporality="1h")
        print("✅ Cliente de Binance inicializado correctamente")
        
        # Obtener precio actual de Bitcoin
        btc_price = robot.symbol_price("BTCUSDT")
        if btc_price:
            print(f"💰 Precio actual de BTC: ${btc_price:,.2f}")
        else:
            print("❌ No se pudo obtener el precio de BTC")
            
        # Probar con algunos símbolos de la configuración
        print("\n📊 Obteniendo precios de las principales criptos:")
        test_symbols = SYMBOLS[:5]  # Primeros 5 símbolos
        
        for symbol in test_symbols:
            price = robot.symbol_price(symbol)
            if price:
                print(f"  {symbol}: ${price:,.4f}")
            else:
                print(f"  {symbol}: ❌ Error obteniendo precio")
                
        # Obtener información de la cuenta (opcional)
        print("\n🏦 Información de la cuenta:")
        try:
            account_info = robot.binance_account()
            print(f"  Balance total: {account_info.get('totalWalletBalance', 'N/A')} USDT")
        except Exception as e:
            print(f"  ⚠️  No se pudo obtener info de cuenta: {str(e)}")
            
        print("\n✅ Prueba completada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error en la prueba: {str(e)}")
        print("💡 Verifica que tus credenciales de API estén configuradas en el archivo .env")

def main():
    test_binance_connection()

if __name__ == "__main__":
    main()