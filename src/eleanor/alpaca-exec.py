import requests, time
from .config import SET

def _hdr():
    return {
        "APCA-API-KEY-ID": SET.alpaca_key_id,
        "APCA-API-SECRET-KEY": SET.alpaca_secret_key,
        "Content-Type": "application/json"
    }

def place_market_order(symbol:str, qty:float, side:str):
    url = f"{SET.alpaca_base_url}/v2/orders"
    payload = {
        "symbol": symbol,
        "qty": str(round(qty,4)),
        "side": side,               # "buy" or "sell"
        "type": "market",
        "time_in_force": "day"
    }
    r = requests.post(url, headers=_hdr(), json=payload, timeout=10)
    r.raise_for_status()
    return r.json()

def get_account():
    r = requests.get(f"{SET.alpaca_base_url}/v2/account", headers=_hdr(), timeout=10)
    r.raise_for_status(); return r.json()

def get_position(symbol:str):
    r = requests.get(f"{SET.alpaca_base_url}/v2/positions/{symbol}", headers=_hdr(), timeout=10)
    if r.status_code==404: return None
    r.raise_for_status(); return r.json()
