from __future__ import annotations

import contextlib
import io
import os
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Protocol

import pandas as pd
import yfinance as yf

from functions import calculate_time_to_expiration


class ProviderError(RuntimeError):
    """Raised when a market data provider cannot return usable data."""


@dataclass(frozen=True)
class PriceQuote:
    ticker: str
    price: float
    currency: str
    source: str
    as_of: str
    note: str = ""


class PriceProvider(Protocol):
    name: str

    def get_spot(self, ticker: str) -> PriceQuote:
        ...

    def get_history(self, ticker: str, days: int = 365) -> pd.DataFrame:
        ...


def _normalize_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        raise ProviderError("Provider returned no price history.")

    normalized = df.copy()
    normalized.columns = [str(column).strip().lower() for column in normalized.columns]
    rename_map = {
        "date": "time",
        "datetime": "time",
        "close_price": "close",
        "open_price": "open",
        "high_price": "high",
        "low_price": "low",
        "volume_accumulated": "volume",
    }
    normalized = normalized.rename(columns=rename_map)

    if "time" not in normalized.columns:
        normalized = normalized.reset_index().rename(columns={"index": "time"})

    required = ["time", "open", "high", "low", "close", "volume"]
    missing = [column for column in required if column not in normalized.columns]
    if missing:
        raise ProviderError(f"History data is missing required columns: {', '.join(missing)}")

    normalized = normalized[required].dropna(subset=["close"])
    normalized["time"] = pd.to_datetime(normalized["time"], errors="coerce")
    normalized = normalized.dropna(subset=["time"]).sort_values("time").reset_index(drop=True)
    if normalized.empty:
        raise ProviderError("Provider returned history, but no usable close prices.")
    return normalized


class YFinanceProvider:
    name = "Yahoo Finance"

    def get_spot(self, ticker: str) -> PriceQuote:
        symbol = ticker.strip().upper()
        history = yf.Ticker(symbol).history(period="5d")
        if history.empty or history["Close"].dropna().empty:
            raise ProviderError(f"No recent Yahoo Finance close price for {symbol}.")

        close = history["Close"].dropna()
        as_of = str(pd.to_datetime(close.index[-1]).date())
        return PriceQuote(symbol, float(close.iloc[-1]), "USD", self.name, as_of)

    def get_history(self, ticker: str, days: int = 365) -> pd.DataFrame:
        symbol = ticker.strip().upper()
        period = "1y" if days <= 366 else "2y"
        history = yf.Ticker(symbol).history(period=period)
        if history.empty:
            raise ProviderError(f"No Yahoo Finance history for {symbol}.")
        history = history.reset_index()
        return _normalize_ohlcv(history)

    def get_option_chains(self, ticker: str) -> tuple[pd.DataFrame, pd.DataFrame, float]:
        symbol = ticker.strip().upper()
        yf_ticker = yf.Ticker(symbol)
        spot_quote = self.get_spot(symbol)
        expirations = list(yf_ticker.options)
        if not expirations:
            raise ProviderError(f"Yahoo Finance has no listed option expirations for {symbol}.")

        calls_frames: list[pd.DataFrame] = []
        puts_frames: list[pd.DataFrame] = []
        for expiry in expirations:
            chain = yf_ticker.option_chain(expiry)
            calls = chain.calls.copy()
            puts = chain.puts.copy()
            calls["expiration"] = expiry
            puts["expiration"] = expiry
            calls_frames.append(calls)
            puts_frames.append(puts)

        calls_all = pd.concat(calls_frames, ignore_index=True)
        puts_all = pd.concat(puts_frames, ignore_index=True)

        columns = ["strike", "lastPrice", "impliedVolatility", "expiration"]
        calls_all = calls_all[columns].dropna()
        puts_all = puts_all[columns].dropna()

        for frame in (calls_all, puts_all):
            frame["time_to_expiration"] = frame["expiration"].apply(calculate_time_to_expiration)

        calls_all = calls_all[
            (calls_all["time_to_expiration"] > 0)
            & (calls_all["impliedVolatility"] > 0)
            & (calls_all["lastPrice"] > 0)
        ].reset_index(drop=True)
        puts_all = puts_all[
            (puts_all["time_to_expiration"] > 0)
            & (puts_all["impliedVolatility"] > 0)
            & (puts_all["lastPrice"] > 0)
        ].reset_index(drop=True)

        if calls_all.empty or puts_all.empty:
            raise ProviderError(f"Yahoo Finance option data for {symbol} has no usable call/put rows.")
        return calls_all, puts_all, spot_quote.price


class VNStockProvider:
    name = "vnstock"

    def __init__(self, source: str = "KBS"):
        self.source = source.strip().upper()

    @contextlib.contextmanager
    def _quiet_vnstock(self):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            yield

    def _quote_client(self, ticker: str):
        try:
            from vnstock.api.quote import Quote
        except Exception as exc:
            raise ProviderError(f"vnstock is unavailable (install/import failed): {exc}") from exc

        symbol = ticker.strip().upper()
        try:
            with self._quiet_vnstock():
                return Quote(symbol=symbol, source=self.source, show_log=False)
        except Exception as exc:
            raise ProviderError(f"vnstock could not initialise {symbol} ({self.source}): {exc}") from exc

    def get_history(self, ticker: str, days: int = 365) -> pd.DataFrame:
        symbol = ticker.strip().upper()
        end = date.today()
        start = end - timedelta(days=days)
        quote = self._quote_client(symbol)
        with self._quiet_vnstock():
            history = quote.history(start=start.isoformat(), end=end.isoformat())
        return _normalize_ohlcv(history)

    def get_spot(self, ticker: str) -> PriceQuote:
        symbol = ticker.strip().upper()
        quote = self._quote_client(symbol)
        intraday_error = ""

        try:
            with self._quiet_vnstock():
                intraday = quote.intraday(page_size=1)
            if intraday is not None and not intraday.empty and "price" in intraday.columns:
                row = intraday.dropna(subset=["price"]).iloc[0]
                return PriceQuote(
                    symbol,
                    float(row["price"]),
                    "VND x1,000 / index points",
                    f"vnstock {self.source}",
                    str(row.get("time", "")),
                    "Intraday price where available.",
                )
        except Exception as exc:  # noqa: BLE001 - provider APIs vary across vnstock releases
            intraday_error = str(exc)

        history = self.get_history(symbol, days=90)
        latest = history.iloc[-1]
        note = "Latest historical close used as spot."
        if intraday_error:
            note += f" Intraday fallback reason: {intraday_error[:90]}"
        return PriceQuote(
            symbol,
            float(latest["close"]),
            "VND x1,000 / index points",
            f"vnstock {self.source}",
            str(latest["time"].date()),
            note,
        )


class FiinQuantProvider:
    name = "FiinQuant"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("FIINQUANT_API_KEY")

    def _raise_stub(self) -> None:
        if not self.api_key:
            raise ProviderError(
                "FiinQuant is documented as an instructor data tier, but FIINQUANT_API_KEY is not configured."
            )
        raise ProviderError("FiinQuant credentials were found, but the provider adapter is intentionally a stub.")

    def get_spot(self, ticker: str) -> PriceQuote:
        self._raise_stub()

    def get_history(self, ticker: str, days: int = 365) -> pd.DataFrame:
        self._raise_stub()
