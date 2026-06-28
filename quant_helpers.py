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
    """Worked, number-by-number Black-Scholes substitution for teaching:
    shows d1, d2, N(d1), N(d2), the discount factors, and the call/put price
    each assembled from those pieces — bridging calculator output and hand
    computation. The resulting Call/Put match the app's priced values."""
    if S <= 0 or K <= 0 or T <= 0 or sigma <= 0:
        return "Enter S > 0, K > 0, T > 0 and sigma > 0 to see the worked substitution."

    d1, d2 = _d1_d2(S, K, r, T, sigma, q)
    sqrt_t = np.sqrt(T)
    n_d1, n_d2 = norm.cdf(d1), norm.cdf(d2)
    n_neg_d1, n_neg_d2 = norm.cdf(-d1), norm.cdf(-d2)
    disc_q, disc_r = np.exp(-q * T), np.exp(-r * T)
    call = S * disc_q * n_d1 - K * disc_r * n_d2
    put = K * disc_r * n_neg_d2 - S * disc_q * n_neg_d1

    return (
        "BLACK-SCHOLES, STEP BY STEP (continuous dividend yield q)\n"
        "--------------------------------------------------------\n"
        f"Inputs:  S = {S:.4f}   K = {K:.4f}   r = {r:.4%}   q = {q:.4%}\n"
        f"         T = {T:.4f} yr   sigma = {sigma:.4%}\n\n"
        "d1 = [ln(S/K) + (r - q + sigma^2/2)·T] / (sigma·sqrt(T))\n"
        f"   = [ln({S:.4f}/{K:.4f}) + ({r:.4f} - {q:.4f} + {sigma ** 2 / 2:.4f})·{T:.4f}]"
        f" / ({sigma:.4f}·{sqrt_t:.4f})\n"
        f"   = {d1:.4f}\n\n"
        f"d2 = d1 - sigma·sqrt(T) = {d1:.4f} - {sigma:.4f}·{sqrt_t:.4f} = {d2:.4f}\n\n"
        f"N(d1) = {n_d1:.4f}     N(d2) = {n_d2:.4f}\n"
        f"e^(-qT) = {disc_q:.4f}     e^(-rT) = {disc_r:.4f}\n\n"
        "Call = S·e^(-qT)·N(d1) - K·e^(-rT)·N(d2)\n"
        f"     = {S:.4f}·{disc_q:.4f}·{n_d1:.4f} - {K:.4f}·{disc_r:.4f}·{n_d2:.4f}\n"
        f"     = {call:.4f}\n\n"
        "Put  = K·e^(-rT)·N(-d2) - S·e^(-qT)·N(-d1)\n"
        f"     = {K:.4f}·{disc_r:.4f}·{n_neg_d2:.4f} - {S:.4f}·{disc_q:.4f}·{n_neg_d1:.4f}\n"
        f"     = {put:.4f}"
    )
