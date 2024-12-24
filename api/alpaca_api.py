import alpaca_trade_api as alpaca
from config.settings import ALPACA_ENDPOINT, ALPACA_KEY, ALPACA_SECRET

def check_alpaca_connection():
    api = alpaca.REST(ALPACA_KEY, ALPACA_SECRET, ALPACA_ENDPOINT)
    account = api.get_account()
    print(account)

