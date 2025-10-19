import numpy as np, pandas as pd  def bollinger(df: pd.DataFrame, window=20, n_sigma=2.0):     m = df['close'].rolling(window).mean()     s = df['close'].rolling(window).std(ddof=0)     upper, lower = m + n_sigma*s, m - n_sigma*s     return m, upper, lower  def macd(df: pd.DataFrame, fast=12, slow=26, signal=9):     ema_fast = df['close'].ewm(span=fast, adjust=False).mean()     ema_slow = df['close'].ewm(span=slow, adjust=False).mean()     macd_line = ema_fast - ema_slow     signal_line = macd_line.ewm(span=signal, adjust=False).mean()     hist = macd_line - signal_line     return macd_line, signal_line, hist  def combined_signal(df: pd.DataFrame):     m, u, l = bollinger(df)     macd_line, signal_line, hist = macd(df)     latest = df.index[-1]     price = df['close'].iloc[-1]     bb_long = price < l.iloc[-1]     bb_short = price > u.iloc[-1]     macd_long = macd_line.iloc[-1] > signal_line.iloc[-1] and hist.iloc[-1] > 0     macd_short = macd_line.iloc[-1] < signal_line.iloc[-1] and hist.iloc[-1] < 0      # Raw intents     long_intent = int(bb_long) + int(macd_long)     short_intent = int(bb_short) + int(macd_short)      # net score: +2 strong long, -2 strong short, else 0/±1     score = long_intent - short_intent     return dict(ts=str(latest), price=float(price), score=int(score),                 bb=(float(l.iloc[-1]), float(u.iloc[-1])), macd=(float(macd_line.iloc[-1]), float(signal_line.iloc[-1])))
import numpy as np, pandas as pd

def bollinger(df: pd.DataFrame, window=20, n_sigma=2.0):
    m = df['close'].rolling(window).mean()
    s = df['close'].rolling(window).std(ddof=0)
    upper, lower = m + n_sigma*s, m - n_sigma*s
    return m, upper, lower

def macd(df: pd.DataFrame, fast=12, slow=26, signal=9):
    ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def combined_signal(df: pd.DataFrame):
    m, u, l = bollinger(df)
    macd_line, signal_line, hist = macd(df)
    latest = df.index[-1]
    price = df['close'].iloc[-1]
    bb_long = price < l.iloc[-1]
    bb_short = price > u.iloc[-1]
    macd_long = macd_line.iloc[-1] > signal_line.iloc[-1] and hist.iloc[-1] > 0
    macd_short = macd_line.iloc[-1] < signal_line.iloc[-1] and hist.iloc[-1] < 0

    # Raw intents
    long_intent = int(bb_long) + int(macd_long)
    short_intent = int(bb_short) + int(macd_short)

    # net score: +2 strong long, -2 strong short, else 0/±1
    score = long_intent - short_intent
    return dict(ts=str(latest), price=float(price), score=int(score), bb=(float(l.iloc[-1]), float(u.iloc[-1])), macd=(float(macd_line.iloc[-1]), float(signal_line.iloc[-1])))
