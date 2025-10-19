import pandas as pd
from math import isfinite

def bayes_weight(signal_scores: pd.Series, outcomes: pd.Series):
    """
    signal_scores: integer scores per trade (-2..+2)
    outcomes: +1 for profitable, 0 else
    Returns posterior P(win | score) for each score bucket and normalized weights.
    """
    df = pd.DataFrame({'s': signal_scores, 'y': outcomes}).dropna()
    pri = df['y'].mean() if len(df) else 0.5  # Laplace prior fallback
    buckets = sorted(df['s'].unique()) if len(df) else [-2,-1,0,1,2]
    post = {}
    for b in buckets:
        sub = df[df['s']==b]
        if len(sub) == 0:
            post[b] = pri
        else:
            # Laplace smoothing
            wins = sub['y'].sum()
            post[b] = (wins + 1) / (len(sub) + 2)
    # normalize to weights
    vals = [post.get(b, pri) for b in [-2,-1,0,1,2]]
    s = sum(vals)
    weights = [v/s if s>0 else 0.2 for v in vals]
    return dict(post=post, weights=dict(zip([-2,-1,0,1,2], weights)))
