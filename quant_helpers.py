from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.stats import norm


@dataclass(frozen=True)
class GreekSnapshot:
    call_delta: float
    put_delta: float
    gamma: float
    vega_per_1pct: float
    call_theta_per_day: float
    put_theta_per_day: float
    call_rho_per_1pct: float
    put_rho_per_1pct: float


@dataclass(frozen=True)
class ParityResult:
    lhs: float
    rhs: float
    gap: float
    tolerance: float
    ok: bool
    formula_label: str


def _d1_d2(S: float, K: float, r: float, T: float, sigma: float, q: float) -> tuple[float, float]:
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return d1, d2


def calculate_greeks(S: float, K: float, r: float, T: float, sigma: float, q: float = 0.0) -> GreekSnapshot:
    if S <= 0 or K <= 0 or T <= 0 or sigma <= 0:
        nan = float("nan")
        return GreekSnapshot(nan, nan, nan, nan, nan, nan, nan, nan)

    d1, d2 = _d1_d2(S, K, r, T, sigma, q)
    discount_q = np.exp(-q * T)
    discount_r = np.exp(-r * T)
    density = norm.pdf(d1)

    gamma = discount_q * density / (S * sigma * np.sqrt(T))
    vega = S * discount_q * density * np.sqrt(T) / 100
    call_theta = (
        -S * discount_q * density * sigma / (2 * np.sqrt(T))
        - r * K * discount_r * norm.cdf(d2)
        + q * S * discount_q * norm.cdf(d1)
    ) / 365
    put_theta = (
        -S * discount_q * density * sigma / (2 * np.sqrt(T))
        + r * K * discount_r * norm.cdf(-d2)
        - q * S * discount_q * norm.cdf(-d1)
    ) / 365

    return GreekSnapshot(
        call_delta=discount_q * norm.cdf(d1),
        put_delta=discount_q * (norm.cdf(d1) - 1),
        gamma=gamma,
        vega_per_1pct=vega,
        call_theta_per_day=call_theta,
        put_theta_per_day=put_theta,
        call_rho_per_1pct=K * T * discount_r * norm.cdf(d2) / 100,
        put_rho_per_1pct=-K * T * discount_r * norm.cdf(-d2) / 100,
    )


def parity_check(
    call_price: float,
    put_price: float,
    S: float,
    K: float,
    r: float,
    T: float,
    q: float = 0.0,
    tolerance: float | None = None,
) -> ParityResult:
    lhs = call_price - put_price
    if abs(q) < 1e-12:
        rhs = S - K * np.exp(-r * T)
        formula = "C - P ≈ S - K·e^(-rT)"
    else:
        rhs = S * np.exp(-q * T) - K * np.exp(-r * T)
        formula = "C - P ≈ S·e^(-qT) - K·e^(-rT)"

    gap = lhs - rhs
    threshold = tolerance if tolerance is not None else max(0.01, abs(S) * 1e-4)
    return ParityResult(lhs=lhs, rhs=rhs, gap=gap, tolerance=threshold, ok=abs(gap) <= threshold, formula_label=formula)


def payoff_table(S: float, K: float, call_premium: float, put_premium: float) -> pd.DataFrame:
    lower = max(0.01, S * 0.5)
    upper = max(lower * 1.5, S * 1.5)
    spots = np.linspace(lower, upper, 80)
    return pd.DataFrame(
        {
            "spot": spots,
            "long_call": np.maximum(spots - K, 0) - call_premium,
            "long_put": np.maximum(K - spots, 0) - put_premium,
            "strike": K,
        }
    )


def greek_table(snapshot: GreekSnapshot) -> pd.DataFrame:
    return pd.DataFrame(
        [
            ("Delta", snapshot.call_delta, snapshot.put_delta, "Approximate price move for a 1-unit move in spot."),
            ("Gamma", snapshot.gamma, snapshot.gamma, "How quickly delta changes as spot changes."),
            ("Vega", snapshot.vega_per_1pct, snapshot.vega_per_1pct, "Approximate price move for a 1 percentage-point volatility move."),
            ("Theta/day", snapshot.call_theta_per_day, snapshot.put_theta_per_day, "Approximate daily time decay, all else equal."),
            ("Rho", snapshot.call_rho_per_1pct, snapshot.put_rho_per_1pct, "Approximate price move for a 1 percentage-point rate move."),
        ],
        columns=["Greek", "Call", "Put", "Plain English"],
    )


def formula_substitution(S: float, K: float, r: float, T: float, sigma: float, q: float) -> str:
    return (
        "Black-Scholes with continuous dividend yield:\n\n"
        "d1 = [ln(S/K) + (r - q + sigma^2/2)T] / (sigma sqrt(T))\n\n"
        "d2 = d1 - sigma sqrt(T)\n\n"
        f"Current inputs: S={S:.4f}, K={K:.4f}, r={r:.4%}, q={q:.4%}, "
        f"T={T:.4f}, sigma={sigma:.4%}."
    )
