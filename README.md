# Dr. Phil's Quant Lab — Options Pricer

Teaching-grade Streamlit app for undergraduate Derivatives at WSU Vietnam. This fork adapts George Dros' original MIT-licensed Black-Scholes Interactive Heatmap into a black-gold Quant Lab interface with separate US and Vietnam market modes.

## Attribution and License

Original app: [George-Dros/Black-Scholes-Interactive-heatmap](https://github.com/George-Dros/Black-Scholes-Interactive-heatmap) by George Dros, MIT License.

This adaptation keeps the original `LICENSE`; new code in this fork is also released under MIT. Data-provider packages and data sources have their own terms. In particular, review `vnstock` terms before redistribution or commercial use.

## What the App Does

- Prices theoretical European calls and puts with the Black-Scholes model.
- Shows a visible put-call parity sanity check.
- Displays Greeks in plain English.
- Builds spot-by-volatility heatmaps.
- Draws expiry payoff diagrams.
- Shows the Black-Scholes formula with the current inputs substituted.
- Keeps US listed-option comparison separate from Vietnam spot-driven theory.

## Market Modes

### Vietnam: spot-driven theory

Vietnam has no exchange-listed single-stock equity options. The VN mode therefore uses real VN spot/history data only to drive theoretical pricing, Greeks, heatmaps, and payoff diagrams.

Supported free/default data path:

- `vnstock==4.0.4`
- Default source: `KBS`
- Alternative source: `VCI`
- Manual spot fallback for class use when data is missing

Useful sample underlyings:

- `FPT`
- `MWG`
- `HPG`
- `VNM`
- `VN30`
- `VNINDEX`

### United States: listed-option demo

The US mode keeps the Yahoo Finance option-chain demo from the upstream app. It compares theoretical Black-Scholes values with real listed-option prices for tickers such as `SPY` or `AAPL`.

### FiinQuant instructor tier

`FiinQuantProvider` is included as a documented swap-in stub. It intentionally does not ship with credentials or paid-data assumptions. Configure `FIINQUANT_API_KEY` only outside the repository if an instructor chooses to implement that adapter.

## Setup

Python runtime used for this fork:

```bash
Python 3.12.10
```

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install pinned dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run main.py
```

## Data and Secrets

- No API keys, tokens, or secrets are committed.
- `.streamlit/secrets.toml`, `.env`, and `.env.*` are ignored.
- The core student path runs on free data via Yahoo Finance and vnstock/manual fallback.

## Files

```text
main.py              Streamlit app
functions.py         Original Black-Scholes and heatmap calculation helpers
data_providers.py    PriceProvider abstraction and US/VN provider implementations
quant_helpers.py     Parity, Greeks, payoff, and formula teaching helpers
charts.py            Dark Quant Lab chart rendering
style.py             Single CSS injection point
.streamlit/config.toml
CHANGELOG.md
```

## Covered Warrant Phase 2

Vietnam covered warrants on HOSE are real single-stock derivatives and can be priced with Black-Scholes-type models adjusted for conversion ratio. This is documented as a high-value phase 2 teaching hook but is not part of the core app path yet.
