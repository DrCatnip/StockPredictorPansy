import pandas as pd


# --------------------------------------------------------
# SIMPLE MOVING AVERAGE
# --------------------------------------------------------

def add_sma(data: pd.DataFrame) -> pd.DataFrame:

    df = data.copy()

    df["SMA20"] = df["Close"].rolling(window=20).mean()
    df["SMA50"] = df["Close"].rolling(window=50).mean()

    return df


# --------------------------------------------------------
# EXPONENTIAL MOVING AVERAGE
# --------------------------------------------------------

def add_ema(data: pd.DataFrame) -> pd.DataFrame:

    df = data.copy()

    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()

    return df


# --------------------------------------------------------
# RSI
# --------------------------------------------------------

def add_rsi(data: pd.DataFrame, period: int = 14):

    df = data.copy()

    delta = df["Close"].diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    df["RSI"] = 100 - (100 / (1 + rs))

    return df


# --------------------------------------------------------
# MACD
# --------------------------------------------------------

def add_macd(data: pd.DataFrame):

    df = data.copy()

    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()

    df["MACD"] = ema12 - ema26
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["Histogram"] = df["MACD"] - df["Signal"]

    return df


# --------------------------------------------------------
# BOLLINGER BANDS
# --------------------------------------------------------

def add_bollinger_bands(data: pd.DataFrame):

    df = data.copy()

    sma = df["Close"].rolling(20).mean()

    std = df["Close"].rolling(20).std()

    df["BB_Upper"] = sma + (2 * std)
    df["BB_Lower"] = sma - (2 * std)

    return df


# --------------------------------------------------------
# ATR
# --------------------------------------------------------

def add_atr(data: pd.DataFrame, period: int = 14):

    df = data.copy()

    high_low = df["High"] - df["Low"]

    high_close = (df["High"] - df["Close"].shift()).abs()

    low_close = (df["Low"] - df["Close"].shift()).abs()

    tr = pd.concat(
        [high_low, high_close, low_close],
        axis=1
    ).max(axis=1)

    df["ATR"] = tr.rolling(period).mean()

    return df


# --------------------------------------------------------
# APPLY ALL INDICATORS
# --------------------------------------------------------

def calculate_indicators(data: pd.DataFrame):

    df = data.copy()

    df = add_sma(df)
    df = add_ema(df)
    df = add_rsi(df)
    df = add_macd(df)
    df = add_bollinger_bands(df)
    df = add_atr(df)

    return df