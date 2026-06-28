from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

import charts
import functions as bs
from data_providers import FiinQuantProvider, ProviderError, VNStockProvider, YFinanceProvider
from quant_helpers import calculate_greeks, formula_substitution, greek_table, parity_check, payoff_table
from style import apply_quantlab_style, render_footer


st.set_page_config(
    page_title="Dr. Phil's Quant Lab — Options Pricer",
    page_icon="⚛",
    layout="wide",
)
apply_quantlab_style()


@st.cache_data(ttl=900, show_spinner=False)
def fetch_vn_spot(ticker: str, source: str):
    return VNStockProvider(source=source).get_spot(ticker)


@st.cache_data(ttl=900, show_spinner=False)
def fetch_vn_history(ticker: str, source: str, days: int):
    return VNStockProvider(source=source).get_history(ticker, days=days)


@st.cache_data(ttl=900, show_spinner=False)
def fetch_us_options(ticker: str):
    return YFinanceProvider().get_option_chains(ticker)


@st.cache_data(ttl=900, show_spinner=False)
def fetch_us_history(ticker: str, days: int):
    return YFinanceProvider().get_history(ticker, days=days)


def money(value: float, currency: str = "") -> str:
    prefix = "$" if currency == "USD" else ""
    suffix = "" if currency == "USD" else f" {currency}".rstrip()
    return f"{prefix}{value:,.2f}{suffix}"


def metric_card(label: str, value: str, note: str = "") -> None:
    st.markdown(
        f"""
        <div class="ql-card">
          <div class="ql-card-label">{label}</div>
          <div class="ql-card-value">{value}</div>
          <div class="ql-card-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_parity_badge(parity) -> None:
    css_class = "ql-badge-ok" if parity.ok else "ql-badge-bad"
    symbol = "✓" if parity.ok else "✗"
    st.markdown(
        f"""
        <span class="ql-badge {css_class}">{symbol} Put-call parity</span>
        <span style="color:#8A8A8A; margin-left:0.6rem;">
          {parity.formula_label}; gap {parity.gap:+.6f}
        </span>
        """,
        unsafe_allow_html=True,
    )


def option_inputs(default_spot: float, default_rate: float) -> tuple[float, float, float, float]:
    strike = st.sidebar.number_input("Strike", min_value=0.01, value=float(round(default_spot, 2)), format="%.2f")
    volatility = st.sidebar.number_input("Volatility (sigma)", min_value=0.01, max_value=3.0, value=0.25, format="%.4f")
    maturity = st.sidebar.number_input("Time to maturity (years)", min_value=0.01, max_value=10.0, value=1.0, format="%.4f")
    risk_free = st.sidebar.number_input(
        "Risk-free rate", min_value=0.0, max_value=1.0, value=default_rate, format="%.4f"
    )
    return strike, volatility, maturity, risk_free


def render_theory_stack(
    *,
    spot: float,
    strike: float,
    volatility: float,
    maturity: float,
    risk_free: float,
    dividend_yield: float,
    currency: str,
    heatmap_mode: str,
    purchase_price: float,
) -> tuple[float, float]:
    call_price = bs.call_bs_value(spot, strike, risk_free, maturity, volatility, q=dividend_yield)
    put_price = bs.put_bs_value(spot, strike, risk_free, maturity, volatility, q=dividend_yield)
    parity = parity_check(call_price, put_price, spot, strike, risk_free, maturity, dividend_yield)

    col1, col2, col3 = st.columns([1, 1, 1.3])
    with col1:
        metric_card("Theoretical call", money(call_price, currency), "Black-Scholes value")
    with col2:
        metric_card("Theoretical put", money(put_price, currency), "Black-Scholes value")
    with col3:
        metric_card("Spot / strike", f"{spot:,.2f} / {strike:,.2f}", f"sigma {volatility:.2%}; T {maturity:.3f} years")

    render_parity_badge(parity)

    st.markdown('<div class="ql-rule"></div>', unsafe_allow_html=True)
    greeks = calculate_greeks(spot, strike, risk_free, maturity, volatility, dividend_yield)

    left, right = st.columns([1.1, 1])
    with left:
        st.subheader("Greeks")
        st.dataframe(
            greek_table(greeks).style.format({"Call": "{:.4f}", "Put": "{:.4f}"}),
            hide_index=True,
            width="stretch",
        )
    with right:
        with st.expander("What each Greek means", expanded=True):
            st.markdown(
                """
                **Delta** is the first-order sensitivity to the underlying price.
                **Gamma** shows how unstable delta becomes as spot moves.
                **Vega** is the sensitivity to a one percentage-point volatility change.
                **Theta** is daily time decay under the current assumptions.
                **Rho** is sensitivity to a one percentage-point rate change.
                """
            )
        with st.expander("Show Black-Scholes formula with current inputs"):
            st.code(formula_substitution(spot, strike, risk_free, maturity, volatility, dividend_yield), language="text")

    spot_min = st.sidebar.number_input("Heatmap min spot", min_value=0.01, value=float(round(0.7 * spot, 2)), format="%.2f")
    spot_max = st.sidebar.number_input(
        "Heatmap max spot",
        min_value=float(max(0.02, spot_min + 0.01)),
        value=float(round(1.3 * spot, 2)),
        format="%.2f",
    )
    vol_min, vol_max = st.sidebar.slider("Heatmap volatility range", 0.01, 1.5, (0.10, 0.60), step=0.01)

    call_df, put_df, call_pnl_df, put_pnl_df = bs.calculate_option_values(
        spot_min,
        spot_max,
        vol_min,
        vol_max,
        strike,
        risk_free,
        maturity,
        dividend_yield=dividend_yield,
        purchase_price=purchase_price,
    )

    st.subheader("Spot × Volatility Heatmap")
    charts.render_value_heatmaps(heatmap_mode, call_df, put_df, call_pnl_df, put_pnl_df)

    st.subheader("Payoff at Expiry")
    payoff = payoff_table(spot, strike, call_premium=call_price, put_premium=put_price)
    charts.render_payoff_chart(payoff)
    return call_price, put_price


def sample_rows(frame: pd.DataFrame, size: int = 11) -> pd.DataFrame:
    frame = frame.sort_values("strike").reset_index(drop=True)
    count = min(size, len(frame))
    indices = np.unique(np.linspace(0, len(frame) - 1, count, dtype=int))
    return frame.iloc[indices].reset_index(drop=True)


st.markdown(
    """
    <div class="ql-header">
      <div class="ql-mark">⚛</div>
      <div>
        <h1 class="ql-title">Dr. Phil's Quant Lab — Options Pricer</h1>
        <p class="ql-subtitle">Black-Scholes teaching lab for undergraduate Derivatives, WSU Vietnam.</p>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.header("Lab Mode")
market_mode = st.sidebar.radio(
    "Market mode",
    ["Vietnam: spot-driven theory", "United States: listed-option demo"],
)

if market_mode == "Vietnam: spot-driven theory":
    st.markdown(
        """
        <div class="ql-note">
        Vietnam has no exchange-listed single-stock equity options, so this mode uses live or recent VN spot data
        for theoretical pricing, Greeks, heatmaps, and payoff diagrams only. Use the US mode for a listed-option
        market-price comparison.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.header("Vietnam Data")
    ticker = st.sidebar.selectbox("Underlying", ["FPT", "MWG", "HPG", "VNM", "VN30", "VNINDEX"], index=0)
    data_choice = st.sidebar.selectbox(
        "Data provider",
        ["vnstock KBS", "vnstock VCI", "Manual input", "FiinQuant instructor tier"],
    )

    quote = None
    history = pd.DataFrame()
    provider_note = ""

    if data_choice.startswith("vnstock"):
        source = data_choice.split()[-1]
        try:
            quote = fetch_vn_spot(ticker, source)
            history = fetch_vn_history(ticker, source, 365)
        except ProviderError as exc:
            provider_note = str(exc)
            st.warning(f"{data_choice} did not return usable data for {ticker}: {exc}")
    elif data_choice.startswith("FiinQuant"):
        try:
            quote = FiinQuantProvider().get_spot(ticker)
        except ProviderError as exc:
            provider_note = str(exc)
            st.info(f"{provider_note} Use manual spot below.")

    default_spot = quote.price if quote else 70.0
    manual_spot = st.sidebar.number_input("Manual spot fallback", min_value=0.01, value=float(default_spot), format="%.2f")
    use_manual_spot = st.sidebar.checkbox("Use manual spot", value=quote is None)
    spot = float(manual_spot if use_manual_spot or quote is None else quote.price)
    currency = "" if ticker in {"VN30", "VNINDEX"} else "VND x1,000"

    st.sidebar.header("Model Inputs")
    strike, volatility, maturity, risk_free = option_inputs(spot, default_rate=0.04)
    dividend_yield = st.sidebar.number_input("Dividend yield", min_value=0.0, max_value=1.0, value=0.0, format="%.4f")
    heatmap_mode = st.sidebar.radio("Heatmap mode", ["Pricing", "P&L"])
    purchase_price = 0.0
    if heatmap_mode == "P&L":
        purchase_price = st.sidebar.number_input("Purchase price / premium", min_value=0.0, value=5.0, format="%.2f")

    data_cols = st.columns(3)
    with data_cols[0]:
        metric_card("Underlying", ticker, data_choice)
    with data_cols[1]:
        metric_card("Spot used", money(spot, currency), "Manual override" if use_manual_spot else quote.note)
    with data_cols[2]:
        as_of = quote.as_of if quote else "Manual"
        metric_card("Data timestamp", as_of, provider_note)

    if not history.empty:
        charts.render_history_chart(history, ticker)

    render_theory_stack(
        spot=spot,
        strike=strike,
        volatility=volatility,
        maturity=maturity,
        risk_free=risk_free,
        dividend_yield=dividend_yield,
        currency=currency,
        heatmap_mode=heatmap_mode,
        purchase_price=purchase_price,
    )

    with st.expander("Phase 2 teaching hook: covered warrants"):
        st.markdown(
            """
            Covered warrants are real single-stock derivatives listed on HOSE and can be priced with
            Black-Scholes-type models after adjusting for the conversion ratio. This app documents that
            route but keeps the core VN mode focused on spot-driven theoretical pricing.
            """
        )

else:
    st.markdown(
        """
        <div class="ql-note">
        This branch keeps the upstream Yahoo Finance idea: compare theoretical Black-Scholes prices with
        real US listed-option prices. It is labelled as a US-market illustration and is not reused for VN
        single-stock options.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.header("US Data")
    ticker = st.sidebar.text_input("US ticker", value="SPY").strip().upper()
    risk_free = st.sidebar.number_input("Risk-free rate", min_value=0.0, max_value=1.0, value=0.03, format="%.4f")
    dividend_yield = st.sidebar.number_input("Dividend yield", min_value=0.0, max_value=1.0, value=0.0, format="%.4f")

    try:
        calls_all, puts_all, spot = fetch_us_options(ticker)
        us_history = fetch_us_history(ticker, 365)
    except ProviderError as exc:
        st.error(f"Could not fetch US option-chain data for {ticker}: {exc}")
        st.stop()

    calls_all["expiration"] = pd.to_datetime(calls_all["expiration"])
    puts_all["expiration"] = pd.to_datetime(puts_all["expiration"])
    common_expiries = sorted(set(calls_all["expiration"]).intersection(set(puts_all["expiration"])))
    if not common_expiries:
        st.error(f"No common call/put expirations found for {ticker}.")
        st.stop()

    selected_expiry = st.sidebar.selectbox(
        "Listed option expiry",
        common_expiries,
        format_func=lambda expiry: pd.to_datetime(expiry).strftime("%Y-%m-%d"),
    )

    date_for_call = calls_all[calls_all["expiration"] == selected_expiry].sort_values("strike").reset_index(drop=True)
    date_for_put = puts_all[puts_all["expiration"] == selected_expiry].sort_values("strike").reset_index(drop=True)
    maturity = float(date_for_call["time_to_expiration"].iloc[0])
    median_iv = pd.concat([date_for_call["impliedVolatility"], date_for_put["impliedVolatility"]]).median()

    atm_index = (date_for_call["strike"] - spot).abs().idxmin()
    default_strike = float(date_for_call.loc[atm_index, "strike"])
    st.sidebar.header("Teaching Inputs")
    strike = st.sidebar.number_input("Parity/payoff strike", min_value=0.01, value=default_strike, format="%.2f")
    volatility = st.sidebar.number_input(
        "Parity/payoff volatility",
        min_value=0.01,
        max_value=3.0,
        value=float(median_iv if pd.notna(median_iv) and median_iv > 0 else 0.25),
        format="%.4f",
    )
    heatmap_mode = "Pricing"
    purchase_price = 0.0

    min_spot, max_spot = st.sidebar.slider(
        "Listed comparison spot range",
        min_value=float(round(0.2 * spot, 2)),
        max_value=float(round(2.0 * spot, 2)),
        value=(float(round(0.7 * spot, 2)), float(round(1.3 * spot, 2))),
        format="%.2f",
    )

    data_cols = st.columns(3)
    with data_cols[0]:
        metric_card("Ticker", ticker, "Yahoo Finance")
    with data_cols[1]:
        metric_card("Spot", money(float(spot), "USD"), "Recent close")
    with data_cols[2]:
        metric_card("Selected expiry", pd.to_datetime(selected_expiry).strftime("%Y-%m-%d"), f"T = {maturity:.3f} years")

    charts.render_history_chart(us_history, ticker)

    render_theory_stack(
        spot=float(spot),
        strike=strike,
        volatility=volatility,
        maturity=maturity,
        risk_free=risk_free,
        dividend_yield=dividend_yield,
        currency="USD",
        heatmap_mode=heatmap_mode,
        purchase_price=purchase_price,
    )

    st.subheader("US Listed-Option Comparison")
    call_datapoints = sample_rows(date_for_call)
    put_datapoints = sample_rows(date_for_put)
    call_df, put_df = bs.calculate_market_prices(
        min_spot,
        max_spot,
        call_datapoints,
        put_datapoints,
        risk_free,
        dividend_yield,
    )
    charts.render_market_heatmaps(call_df.round(2), put_df.round(2))

    with st.expander("Sampled option rows used in the comparison"):
        c1, c2 = st.columns(2)
        with c1:
            st.caption("Calls")
            st.dataframe(call_datapoints, hide_index=True, width="stretch")
        with c2:
            st.caption("Puts")
            st.dataframe(put_datapoints, hide_index=True, width="stretch")


render_footer()
