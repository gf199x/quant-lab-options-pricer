from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm


BG = "#0B0B0C"
SURFACE = "#15161A"
GOLD = "#C8A04E"
TEXT = "#EDEDED"
MUTED = "#8A8A8A"
TEAL = "#4FB0AE"
WINE = "#7E2F3A"

VALUE_CMAP = LinearSegmentedColormap.from_list("quantlab_value", [SURFACE, "#21373A", GOLD])
PNL_CMAP = LinearSegmentedColormap.from_list("quantlab_pnl", [WINE, SURFACE, GOLD, TEAL])
MISPRICING_CMAP = LinearSegmentedColormap.from_list("quantlab_mispricing", [WINE, SURFACE, GOLD])


def _style_figure(fig: plt.Figure, axes) -> None:
    fig.patch.set_facecolor(BG)
    for ax in axes:
        ax.set_facecolor(SURFACE)
        ax.tick_params(colors=MUTED, labelsize=9)
        for spine in ax.spines.values():
            spine.set_color("#2A2C32")
        ax.xaxis.label.set_color(MUTED)
        ax.yaxis.label.set_color(MUTED)
        ax.title.set_color(TEXT)


def _style_heatmap_colorbar(fig: plt.Figure) -> None:
    for ax in fig.axes:
        if ax.collections:
            colorbar = ax.collections[0].colorbar
            if colorbar:
                colorbar.ax.yaxis.set_tick_params(color=MUTED)
                plt.setp(colorbar.ax.get_yticklabels(), color=MUTED)
                colorbar.outline.set_edgecolor("#2A2C32")


def render_value_heatmaps(mode: str, call_df: pd.DataFrame, put_df: pd.DataFrame, call_pnl_df=None, put_pnl_df=None) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(18, 8))
    _style_figure(fig, axes)

    if mode == "P&L":
        data = [(call_pnl_df, "Long Call P&L"), (put_pnl_df, "Long Put P&L")]
        cmap = PNL_CMAP
        vmin = min(frame.min().min() for frame, _ in data)
        vmax = max(frame.max().max() for frame, _ in data)
        norm = TwoSlopeNorm(vcenter=0, vmin=vmin, vmax=vmax) if vmin < 0 < vmax else None
    else:
        data = [(call_df, "Call Prices"), (put_df, "Put Prices")]
        cmap = VALUE_CMAP
        norm = None

    for ax, (frame, title) in zip(axes, data):
        sns.heatmap(
            frame,
            ax=ax,
            cmap=cmap,
            norm=norm,
            annot=True,
            cbar=True,
            fmt=".2f",
            linewidths=0.35,
            linecolor="#2A2C32",
            annot_kws={"color": TEXT, "fontsize": 8},
        )
        ax.set_title(title, pad=16, fontsize=15)
        ax.set_xlabel("Spot")
        ax.set_ylabel("Volatility")

    _style_heatmap_colorbar(fig)
    fig.tight_layout()
    st.pyplot(fig)


def render_market_heatmaps(call_df: pd.DataFrame, put_df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(18, 8))
    _style_figure(fig, axes)
    combined_min = min(call_df.min().min(), put_df.min().min())
    combined_max = max(call_df.max().max(), put_df.max().max())
    norm = TwoSlopeNorm(vcenter=0, vmin=combined_min, vmax=combined_max) if combined_min < 0 < combined_max else None

    for ax, frame, title in zip(axes, [call_df, put_df], ["Call: theoretical minus market", "Put: theoretical minus market"]):
        sns.heatmap(
            frame,
            ax=ax,
            cmap=MISPRICING_CMAP,
            norm=norm,
            annot=True,
            cbar=True,
            fmt=".2f",
            linewidths=0.35,
            linecolor="#2A2C32",
            annot_kws={"color": TEXT, "fontsize": 8},
        )
        ax.set_title(title, pad=16, fontsize=15)
        ax.set_xlabel("Spot")
        ax.set_ylabel("Implied volatility")

    _style_heatmap_colorbar(fig)
    fig.tight_layout()
    st.pyplot(fig)


def render_history_chart(history: pd.DataFrame, ticker: str) -> None:
    if history is None or history.empty:
        return

    fig, ax = plt.subplots(figsize=(12, 4.4))
    _style_figure(fig, [ax])
    ax.plot(history["time"], history["close"], color=GOLD, linewidth=2.2)
    ax.fill_between(history["time"], history["close"], color=GOLD, alpha=0.08)
    ax.set_title(f"{ticker.upper()} close history", pad=14)
    ax.set_xlabel("")
    ax.set_ylabel("Close")
    fig.autofmt_xdate(rotation=0, ha="center")
    fig.tight_layout()
    st.pyplot(fig)


def render_payoff_chart(payoff: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(12, 4.8))
    _style_figure(fig, [ax])
    ax.axhline(0, color="#3A3D45", linewidth=1)
    ax.axvline(payoff["strike"].iloc[0], color=MUTED, linestyle="--", linewidth=1)
    ax.plot(payoff["spot"], payoff["long_call"], color=GOLD, linewidth=2.2, label="Long call")
    ax.plot(payoff["spot"], payoff["long_put"], color=TEAL, linewidth=2.2, label="Long put")
    ax.set_title("Expiry payoff, net of selected premium", pad=14)
    ax.set_xlabel("Spot at expiry")
    ax.set_ylabel("Payoff")
    legend = ax.legend(facecolor=SURFACE, edgecolor="#2A2C32")
    for text in legend.get_texts():
        text.set_color(TEXT)
    fig.tight_layout()
    st.pyplot(fig)
