import numpy as np, pandas as pd

def sharpe_ratio(returns: pd.Series, rf=0.0):
    if len(returns) < 2: return 0.0
    ex = returns - rf/252.0
    return float(np.sqrt(252) * ex.mean() / (ex.std(ddof=1) + 1e-9))

def position_size(score:int, weights:dict, max_gross:float=1.0):
    # Map -2..+2 into 0..1 long exposure via Bayesian weights
    # Negative scores will be zeroed for long-only equities.
    w = weights.get(score, 0.2)
    return float(min(max(w*max_gross, 0.0), max_gross))
