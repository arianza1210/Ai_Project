import yfinance as yf

class YFinance:
    def __init__(self):
        pass

    def fetch_price_data(self, ticker):
        tk = yf.Ticker(ticker)
        df = tk.history(period="90d", interval="1d")
        df = df.dropna()
        return df

    def compute_indicators(self, df):
        out = {}
        close = df["Close"]
        out["Close"] = close.iloc[-1]
        out["PrevClose"] = close.shift(1).iloc[-1]
        out["PctChange"] = round((out["Close"] - out["PrevClose"]) / out["PrevClose"] * 100, 2)
        out["SMA10"] = close.rolling(10).mean().iloc[-1]  # Untuk trend jangka pendek
        out["SMA20"] = close.rolling(20).mean().iloc[-1]
        out["SMA50"] = close.rolling(50).mean().iloc[-1]

        # RSI
        delta = close.diff()
        up = delta.clip(lower=0)
        down = -delta.clip(upper=0)
        roll_up = up.rolling(14).mean()
        roll_down = down.rolling(14).mean()
        rs = roll_up / (roll_down + 1e-9)
        out["RSI14"] = round(100 - (100 / (1 + rs.iloc[-1])), 2)

        # MACD
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd_line = ema12 - ema26
        signal = macd_line.ewm(span=9, adjust=False).mean()
        out["MACD"] = round(macd_line.iloc[-1], 4)
        out["MACD_signal"] = round(signal.iloc[-1], 4)

        # Volume
        out["Volume"] = int(df["Volume"].iloc[-1])
        out["AvgVolume20"] = int(df["Volume"].rolling(20).mean().iloc[-1])
        out["VolumeRatio"] = round(out["Volume"] / (out["AvgVolume20"] + 1e-9), 2)
        
        # Stochastic 14, 3, 3
        low14 = df["Low"].rolling(14).min()
        high14 = df["High"].rolling(14).max()

        stoch_k = ((df["Close"] - low14) / (high14 - low14 + 1e-9)) * 100
        stoch_k = stoch_k.rolling(3).mean()  

        stoch_d = stoch_k.rolling(3).mean()  

        out["StochK"] = round(stoch_k.iloc[-1], 2)
        out["StochD"] = round(stoch_d.iloc[-1], 2)

        # Pivot Fibonacci (type=fibonacci, numberOfPivot=1)
        last_high = df["High"].iloc[-1]
        last_low = df["Low"].iloc[-1]
        last_close = df["Close"].iloc[-1]

        pivot = (last_high + last_low + last_close) / 3
        rng = last_high - last_low

        out["Pivot"] = round(pivot, 2)

        # Fibonacci Resistance Levels
        out["R1"] = round(pivot + 0.382 * rng, 2)
        out["R2"] = round(pivot + 0.618 * rng, 2)
        out["R3"] = round(pivot + 1.000 * rng, 2)

        # Fibonacci Support Levels
        out["S1"] = round(pivot - 0.382 * rng, 2)
        out["S2"] = round(pivot - 0.618 * rng, 2)
        out["S3"] = round(pivot - 1.000 * rng, 2)
        # EMA untuk respons lebih cepat
        out["EMA9"] = close.ewm(span=9, adjust=False).mean().iloc[-1]
        out["EMA21"] = close.ewm(span=21, adjust=False).mean().iloc[-1]
        out["Resistance"] = df["High"].rolling(20).max().iloc[-1]  # 20-day high
        out["Support"] = df["Low"].rolling(20).min().iloc[-1]     # 20-day low

        return out

    def fetch_fundamentals(self, ticker):
        info = yf.Ticker(ticker).info
        return {
            "marketCap": info.get("marketCap"),
            "enterpriseValue": info.get("enterpriseValue"),
            "trailingPE": info.get("trailingPE"),
            "forwardPE": info.get("forwardPE"),
            "pegRatio": info.get("pegRatio"),

            # profitability
            "profitMargins": info.get("profitMargins"),
            "grossMargins": info.get("grossMargins"),
            "operatingMargins": info.get("operatingMargins"),
            "returnOnAssets": info.get("returnOnAssets"),
            "returnOnEquity": info.get("returnOnEquity"),

            # growth
            "revenueGrowth": info.get("revenueGrowth"),
            "earningsGrowth": info.get("earningsGrowth"),
            "earningsQuarterlyGrowth": info.get("earningsQuarterlyGrowth"),

            # balance sheet
            "totalCash": info.get("totalCash"),
            "totalDebt": info.get("totalDebt"),
            "debtToEquity": info.get("debtToEquity"),
            "currentRatio": info.get("currentRatio"),
            "quickRatio": info.get("quickRatio"),

            # cash flow
            "operatingCashflow": info.get("operatingCashflow"),
            "freeCashflow": info.get("freeCashflow"),
            "ebitda": info.get("ebitda"),

            # dividend
            "dividendRate": info.get("dividendRate"),
            "dividendYield": info.get("dividendYield"),
            "payoutRatio": info.get("payoutRatio"),

            # company info
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "longName": info.get("longName"),
            "fullTimeEmployees": info.get("fullTimeEmployees"),
            "country": info.get("country"),
            "website": info.get("website"),
        }


    def format_stock_data(self, ticker):
        try:
            df = self.fetch_price_data(ticker)
            if df.empty:
                return {
                    "ticker": ticker,
                    "error": "Data harga tidak tersedia"
                }

            indicators = self.compute_indicators(df)
            fundamentals = self.fetch_fundamentals(ticker)

            # --- helper format marketcap ---
            def format_marketcap(mc):
                if not mc:
                    return "N/A"
                if mc >= 1e12:
                    return f"{mc / 1e12:.2f} T"
                elif mc >= 1e9:
                    return f"{mc / 1e9:.2f} B"
                elif mc >= 1e6:
                    return f"{mc / 1e6:.2f} M"
                return f"{mc:,}"

            technical_md = f"""
## {ticker}
### Indikator Teknikal Terkini

| Indikator         | Nilai |
|-------------------|--------------|
| Close             | {indicators["Close"]:,.2f} |
| % Change (1 hari) | {indicators["PctChange"]:+.2f}% |
| SMA10             | {indicators["SMA10"]:,.2f} |
| SMA20             | {indicators["SMA20"]:,.2f} |
| SMA50             | {indicators["SMA50"]:,.2f} |
| RSI14             | {indicators["RSI14"]:.2f} |
| EMA9              | {indicators["EMA9"]:.2f} |
| EMA21             | {indicators["EMA21"]:.2f} |
| Resistance        | {indicators["Resistance"]:.2f} |
| Support           | {indicators["Support"]:.2f} |
| MACD              | {indicators["MACD"]:+.4f} |
| MACD Signal       | {indicators["MACD_signal"]:+.4f} |
| Volume Ratio      | {indicators["VolumeRatio"]:.2f}x |
| Stochastic %K     | {indicators["StochK"]:.2f} |
| Stochastic %D     | {indicators["StochD"]:.2f} |
| Pivot (Fib)       | {indicators["Pivot"]:.2f} |
| R1                | {indicators["R1"]:.2f} |
| R2                | {indicators["R2"]:.2f} |
| R3                | {indicators["R3"]:.2f} |
| S1                | {indicators["S1"]:.2f} |
| S2                | {indicators["S2"]:.2f} |
| S3                | {indicators["S3"]:.2f} |
"""

            # --- Markdown Fundamentals ---
            fundamental_md = f"""
### Fundamental Singkat

- **Nama Perusahaan:** {fundamentals.get("longName") or ticker}
- **Sektor:** {fundamentals.get("sector") or 'N/A'}
- **Market Cap:** {format_marketcap(fundamentals.get("marketCap"))}
- **Trailing P/E:** {fundamentals.get("trailingPE") or 'N/A'}
- **Forward P/E:** {fundamentals.get("forwardPE") or 'N/A'}
- **PEG Ratio:** {fundamentals.get("pegRatio") or 'N/A'}

#### Profitabilitas
- **Profit Margin:** {fundamentals.get("profitMargins") or 'N/A'}
- **ROE:** {fundamentals.get("returnOnEquity") or 'N/A'}
- **ROA:** {fundamentals.get("returnOnAssets") or 'N/A'}

#### Balance Sheet
- **Debt to Equity:** {fundamentals.get("debtToEquity") or 'N/A'}
- **Current Ratio:** {fundamentals.get("currentRatio") or 'N/A'}

#### Pertumbuhan
- **Revenue Growth:** {fundamentals.get("revenueGrowth") or 'N/A'}
- **Earnings Growth:** {fundamentals.get("earningsGrowth") or 'N/A'}
"""


            return {
                "ticker": ticker,
                "technical_markdown": technical_md.strip(),
                "fundamental_markdown": fundamental_md.strip(),
                "technical_data": indicators,
                "fundamental_data": fundamentals,
                "full_markdown": (technical_md + "\n" + fundamental_md).strip()
            }

        except Exception as e:
            return {
                "ticker": ticker,
                "error": str(e)
            }


if __name__ == "__main__":
    import json
    yfin = YFinance()
    data = yfin.format_stock_data("BUMI.JK")
    with open("test.json", "w") as f:
        json.dump(data, f, indent=4)
    print(data["technical_markdown"])
    print(data["fundamental_markdown"])
    print(data["technical_data"])       # untuk reasoning LLM
    print(data["fundamental_data"])  
