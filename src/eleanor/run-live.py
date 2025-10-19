import json, math, pandas as pd
from eleanor.config import SET
from eleanor.data import fetch_ohlc
from eleanor.signals import combined_signal
from eleanor.bayes import bayes_weight
from eleanor.sizing import position_size
from eleanor.alpaca_exec import get_account, get_position, place_market_order

WATCH = ["AAPL","MSFT","NVDA","SPY","QQQ"]  # example equities universe

# Simple PnL store for posterior updates (append-only csv)
HIST_CSV = "./data/trade_history.csv"

def load_history():
    try: return pd.read_csv(HIST_CSV)
    except: return pd.DataFrame(columns=["ts","symbol","score","ret"])

def save_trade(ts,symbol,score,ret):
    df = load_history()
    df.loc[len(df)] = [ts,symbol,score,ret]
    df.to_csv(HIST_CSV, index=False)

def calc_qty(equity, target_weight, price):
    target_notional = equity * target_weight
    return max(0, math.floor(target_notional / price))

def main():
    acct = get_account()
    equity = float(acct["equity"])
    hist = load_history()
    posts = None
    if len(hist)>10:
        posts = bayes_weight(hist["score"].astype(int), (hist["ret"]>0).astype(int))["weights"]
    else:
        posts = {-2:0.1,-1:0.15,0:0.2,1:0.25,2:0.3}

    results = []
    for sym in WATCH:
        df = fetch_ohlc(sym, interval="1h", lookback_days=45)
        sig = combined_signal(df)
        w = position_size(sig["score"], posts, max_gross=0.2)  # cap per-asset at 20%
        px = sig["price"]
        qty = calc_qty(equity, w, px)

        # naive policy: buy on score>=1, sell all on score<=-1
        side = None
        if sig["score"]>=1 and qty>0: side="buy"
        elif sig["score"]<=-1:
            pos = get_position(sym)
            if pos:
                qty = float(pos["qty"])
                side="sell"

        action=None
        if side:
            action = place_market_order(sym, qty, side)
        results.append({"symbol":sym, "score":sig["score"], "weight":w, "price":px, "order":bool(action)})

    print(json.dumps({"ok":True,"results":results}, indent=2))

if __name__ == "__main__":
    main()
