from iqoptionapi.stable_api import IQ_Option
import time
import pandas as pd

# 🔹 Configurações
SYMBOL = "GBPJPY-OTC" 
IQ_EMAIL = "e-mail"
IQ_PASSWORD = "senha"

# 🔹 Função para obter preço atual
def obter_preco_atual():
    try:
        velas = iq_api.get_candles(SYMBOL, 60, 1, time.time())
        return velas[0]['close']
    except Exception as e:
        print("❌ Erro ao obter preço:", e)
        return None

# 🔹 Função para calcular EMA
def calcular_ema(df, periodo):
    return df["close"].ewm(span=periodo, adjust=False).mean()

# 🔹 Conectar à API
print("🔗 Conectando...")
iq_api = IQ_Option(IQ_EMAIL, IQ_PASSWORD)
iq_api.connect()
iq_api.change_balance("REAL")

if not iq_api.check_connect():
    print("❌ Falha de conexão.")
    exit()
print("✅ Conectado!")

# 🔹 Verificar saldo
saldo = iq_api.get_balance()
print("💰 Saldo:", saldo)

# 🔄 Loop de análise
historico_precos = []
while True:
    preco = obter_preco_atual()
    if preco:
        historico_precos.append(preco)
        historico_precos = historico_precos[-50:]  # Limitar histórico a 50 preços

        df = pd.DataFrame(historico_precos, columns=["close"])
        df["EMA9"] = calcular_ema(df, 9)
        df["EMA21"] = calcular_ema(df, 21)

        print(f"\n📊 Preço: {preco:.5f} | EMA9: {df['EMA9'].iloc[-1]:.5f} | EMA21: {df['EMA21'].iloc[-1]:.5f}")

        sinal = None
        if len(df) > 2:
            if df["EMA9"].iloc[-1] > df["EMA21"].iloc[-1] and df["EMA9"].iloc[-2] <= df["EMA21"].iloc[-2]:
                print("🔼 COMPRA detectada!")
                sinal = "CALL"
            elif df["EMA9"].iloc[-1] < df["EMA21"].iloc[-1] and df["EMA9"].iloc[-2] >= df["EMA21"].iloc[-2]:
                print("🔽 VENDA detectada!")
                sinal = "PUT"

            if sinal:
                exp_time = 1  # Tempo de expiração fixo de 1 minuto
                status, id = iq_api.buy_digital_spot(SYMBOL, 5, sinal.upper(), exp_time)
                print(f"✅ Operação ID {id} executada!" if status else "❌ Falha ao executar operação!")

                if not status:
                    print("❌ Falha ao executar operação! Detalhes do erro:")
                    print(f"Status: {status}, ID: {id}")
                else:
                    print(f"✅ Operação ID {id} executada com sucesso!")

    print("⏳ Aguardando...")
    time.sleep(40)
