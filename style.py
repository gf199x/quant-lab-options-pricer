from __future__ import annotations

import streamlit as st


def apply_quantlab_style() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

        :root {
          --ql-bg: #0B0B0C;
          --ql-surface: #15161A;
          --ql-surface-2: #1D1E24;
          --ql-gold: #C8A04E;
          --ql-text: #EDEDED;
          --ql-muted: #8A8A8A;
          --ql-line: #34302A;
          --ql-good: #4FB0AE;
          --ql-bad: #B65A5C;
        }

        html, body, [data-testid="stAppViewContainer"] {
          background: var(--ql-bg);
          color: var(--ql-text);
          font-family: Inter, system-ui, sans-serif;
        }

        [data-testid="stSidebar"] {
          background: #101113;
          border-right: 1px solid var(--ql-line);
        }

        [data-testid="stSidebar"] * {
          font-family: Inter, system-ui, sans-serif;
        }

        h1, h2, h3 {
          font-family: "Playfair Display", Georgia, serif;
          letter-spacing: 0;
        }

        .block-container {
          padding-top: 2rem;
          padding-bottom: 3rem;
          max-width: 1280px;
        }

        .ql-header {
          border-bottom: 1px solid rgba(200, 160, 78, 0.5);
          border-top: 1px solid rgba(200, 160, 78, 0.28);
          padding: 1.2rem 0 1.1rem 0;
          margin-bottom: 1.25rem;
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .ql-mark {
          width: 2.7rem;
          height: 2.7rem;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          border: 1px solid var(--ql-gold);
          color: var(--ql-gold);
          font-size: 1.5rem;
          font-family: "Playfair Display", Georgia, serif;
        }

        .ql-title {
          margin: 0;
          color: var(--ql-text);
          font-family: "Playfair Display", Georgia, serif;
          font-size: clamp(1.9rem, 3vw, 3rem);
          font-weight: 700;
        }

        .ql-subtitle {
          color: var(--ql-muted);
          margin: 0.2rem 0 0 0;
          font-size: 0.95rem;
        }

        .ql-rule {
          height: 1px;
          background: linear-gradient(90deg, transparent, var(--ql-gold), transparent);
          margin: 1.5rem 0;
          opacity: 0.65;
        }

        .ql-card {
          background: var(--ql-surface);
          border: 1px solid #2B2C31;
          border-radius: 8px;
          padding: 1rem 1.05rem;
          min-height: 7rem;
        }

        .ql-card-label {
          color: var(--ql-muted);
          font-size: 0.78rem;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          margin-bottom: 0.45rem;
        }

        .ql-card-value {
          color: var(--ql-text);
          font-size: 1.85rem;
          font-weight: 700;
          line-height: 1.1;
        }

        .ql-card-note {
          color: var(--ql-muted);
          font-size: 0.82rem;
          margin-top: 0.5rem;
        }

        .ql-badge {
          display: inline-flex;
          align-items: center;
          border-radius: 999px;
          padding: 0.32rem 0.62rem;
          font-size: 0.82rem;
          font-weight: 700;
          border: 1px solid;
        }

        .ql-badge-ok {
          color: var(--ql-good);
          border-color: rgba(79, 176, 174, 0.7);
          background: rgba(79, 176, 174, 0.08);
        }

        .ql-badge-bad {
          color: var(--ql-bad);
          border-color: rgba(182, 90, 92, 0.7);
          background: rgba(182, 90, 92, 0.08);
        }

        .ql-note {
          border-left: 2px solid var(--ql-gold);
          padding: 0.75rem 1rem;
          background: rgba(200, 160, 78, 0.08);
          color: var(--ql-text);
          margin: 0.8rem 0 1.1rem 0;
        }

        .ql-footer {
          margin-top: 2.5rem;
          padding-top: 1rem;
          border-top: 1px solid rgba(200, 160, 78, 0.35);
          color: var(--ql-muted);
          font-size: 0.85rem;
        }

        div[data-testid="stMetric"] {
          background: var(--ql-surface);
          border: 1px solid #2B2C31;
          border-radius: 8px;
          padding: 0.85rem 1rem;
        }

        .stDataFrame {
          border: 1px solid #2B2C31;
          border-radius: 8px;
        }

        button[kind="secondary"], div[data-testid="stButton"] button {
          border-color: var(--ql-gold);
          color: var(--ql-text);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    st.markdown(
        """
        <div class="ql-footer">
          Adapted for Dr. Phil's Quant Lab, WSU Vietnam. Original MIT-licensed
          Streamlit app by George Dros: Black-Scholes-Interactive-heatmap.
        </div>
        """,
        unsafe_allow_html=True,
    )
