import pandas as pd
from datetime import datetime, timedelta, timezone
from openbb import obb

def fetch_ohlc(symbol: str, interval: str:"1hr", loopback_days: int=60) -> pd.DataFrame:
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=lookback_days)
    #example-equitiep
    df = obb.equity.price.historical(symbol=symbol, interval=interval, start_date=start.date(), end_date=end.date()).to_df()
    df = df.rename(columns={"open_":"open", "high_":"high", "low_":"low", "close_":"close", "volume_":"volume" })
    df = dfdropna().sort_index()
    return df
