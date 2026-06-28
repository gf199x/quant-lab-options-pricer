"""
style.py - Dr. Phil's Quant Lab design system (black-gold art-deco).

This merged version keeps the richer native Streamlit theming from the
reference design system while preserving the custom Quant Lab classes rendered
directly by main.py.
"""

from __future__ import annotations

import streamlit as st


_ROOT_TOKENS = """
:root {
    --ql-bg:        #0B0B0C;
    --ql-surface:   #15161A;
    --ql-surface-2: #1E2027;
    --ql-gold:      #C8A04E;
    --ql-gold-soft: #E0C079;
    --ql-text:      #EDEDED;
    --ql-muted:     #8A8A8A;
    --ql-line:      rgba(200, 160, 78, 0.28);
    --ql-good:      #4FB0AE;
    --ql-bad:       #B65A5C;
    --ql-radius:    10px;
    --ql-serif:     'Playfair Display', 'Cormorant Garamond', Georgia, serif;
    --ql-body:      'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif;
}
"""

_FONTS = (
    "@import url('https://fonts.googleapis.com/css2?"
    "family=Playfair+Display:wght@500;600;700&"
    "family=Cormorant+Garamond:wght@500;600&"
    "family=Inter:wght@300;400;500;600;700&display=swap');"
)

_CSS = f"""
<style>
{_FONTS}
{_ROOT_TOKENS}

/* ---- App canvas -------------------------------------------------------- */
.stApp,
html,
body,
[data-testid="stAppViewContainer"] {{
    background: var(--ql-bg);
    color: var(--ql-text);
    font-family: var(--ql-body);
}}

.block-container {{
    padding-top: 2.2rem;
    padding-bottom: 3rem;
    max-width: 1180px;
}}

#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}
[data-testid="stHeader"] {{ background: transparent; }}

/* ---- Typography -------------------------------------------------------- */
h1, h2, h3 {{
    font-family: var(--ql-serif);
    color: var(--ql-gold);
    letter-spacing: 0;
    font-weight: 600;
}}

h1 {{ font-size: 2.1rem; }}
h2 {{ font-size: 1.5rem; color: var(--ql-gold-soft); }}
h3 {{ font-size: 1.2rem; color: var(--ql-text); }}
p, label, .stMarkdown {{
    font-family: var(--ql-body);
    color: var(--ql-text);
}}
small, .ql-muted {{ color: var(--ql-muted); }}
a {{ color: var(--ql-gold-soft); }}
a:hover {{ color: var(--ql-gold); }}

/* ---- Sidebar ----------------------------------------------------------- */
[data-testid="stSidebar"] {{
    background: var(--ql-surface);
    border-right: 1px solid var(--ql-line);
}}

[data-testid="stSidebar"] * {{
    font-family: var(--ql-body);
}}

[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2 {{
    font-size: 1.05rem;
}}

/* ---- Inputs: sliders, number, text, select ----------------------------- */
[data-baseweb="slider"] [role="slider"] {{
    background: var(--ql-gold);
    border-color: var(--ql-gold);
}}

.stSlider [data-baseweb="slider"] > div > div {{
    background: var(--ql-gold);
}}

input,
textarea,
[data-baseweb="input"] input,
[data-baseweb="select"] > div {{
    background: var(--ql-surface) !important;
    color: var(--ql-text) !important;
    border: 1px solid var(--ql-line) !important;
    border-radius: var(--ql-radius) !important;
}}

[data-baseweb="select"] svg,
[data-baseweb="checkbox"] svg {{
    color: var(--ql-gold);
}}

/* ---- Buttons ----------------------------------------------------------- */
.stButton > button {{
    background: transparent;
    color: var(--ql-gold);
    border: 1px solid var(--ql-gold);
    border-radius: var(--ql-radius);
    padding: 0.45rem 1.1rem;
    font-family: var(--ql-body);
    font-weight: 500;
    letter-spacing: 0.04em;
    transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}}

.stButton > button:hover {{
    background: var(--ql-gold);
    color: var(--ql-bg);
    border-color: var(--ql-gold);
}}

/* ---- Native metric cards ---------------------------------------------- */
[data-testid="stMetric"] {{
    background: var(--ql-surface);
    border: 1px solid var(--ql-line);
    border-radius: var(--ql-radius);
    padding: 1rem 1.1rem;
}}

[data-testid="stMetricLabel"] {{
    color: var(--ql-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 0.72rem;
}}

[data-testid="stMetricValue"] {{
    color: var(--ql-gold-soft);
    font-family: var(--ql-serif);
    font-weight: 600;
}}

/* ---- Tabs -------------------------------------------------------------- */
.stTabs [data-baseweb="tab-list"] {{
    gap: 1.4rem;
    border-bottom: 1px solid var(--ql-line);
}}

.stTabs [data-baseweb="tab"] {{
    color: var(--ql-muted);
    font-family: var(--ql-body);
    letter-spacing: 0.04em;
}}

.stTabs [aria-selected="true"] {{
    color: var(--ql-gold) !important;
}}

.stTabs [data-baseweb="tab-highlight"] {{
    background: var(--ql-gold);
}}

/* ---- Expander ---------------------------------------------------------- */
[data-testid="stExpander"] {{
    border: 1px solid var(--ql-line);
    border-radius: var(--ql-radius);
    background: var(--ql-surface);
}}

[data-testid="stExpander"] summary {{
    color: var(--ql-gold-soft);
    font-family: var(--ql-body);
}}

/* ---- Dataframe --------------------------------------------------------- */
[data-testid="stDataFrame"],
.stDataFrame {{
    border: 1px solid var(--ql-line);
    border-radius: var(--ql-radius);
}}

/* ---- Quant Lab header / rule / custom cards --------------------------- */
.ql-header {{
    border-top: 1px solid var(--ql-line);
    border-bottom: 1px solid rgba(200, 160, 78, 0.5);
    padding: 1.15rem 0 1.05rem 0;
    margin: 0 0 1.25rem 0;
    display: flex;
    align-items: center;
    gap: 1rem;
}}

.ql-mark {{
    width: 2.7rem;
    height: 2.7rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: 1px solid var(--ql-gold);
    color: var(--ql-gold);
    font-family: var(--ql-serif);
    font-size: 1.45rem;
    line-height: 1;
    flex: 0 0 auto;
}}

.ql-title {{
    margin: 0;
    color: var(--ql-text);
    font-family: var(--ql-serif);
    font-size: 2.35rem;
    font-weight: 700;
    line-height: 1.08;
}}

.ql-subtitle,
.ql-sub {{
    color: var(--ql-muted);
    margin: 0.25rem 0 0 0;
    font-size: 0.82rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}}

.ql-rule {{
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--ql-gold), transparent);
    margin: 1.5rem 0;
    opacity: 0.7;
}}

.ql-card {{
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.025), rgba(255, 255, 255, 0)) var(--ql-surface);
    border: 1px solid var(--ql-line);
    border-radius: 8px;
    padding: 1rem 1.05rem;
    min-height: 7rem;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.035);
}}

.ql-card-label {{
    color: var(--ql-muted);
    font-size: 0.74rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.45rem;
}}

.ql-card-value {{
    color: var(--ql-gold-soft);
    font-family: var(--ql-serif);
    font-size: 1.85rem;
    font-weight: 700;
    line-height: 1.1;
}}

.ql-card-note {{
    color: var(--ql-muted);
    font-size: 0.82rem;
    margin-top: 0.55rem;
}}

.ql-badge {{
    display: inline-flex;
    align-items: center;
    border-radius: 999px;
    padding: 0.32rem 0.62rem;
    font-size: 0.82rem;
    font-weight: 700;
    border: 1px solid;
}}

.ql-badge-ok {{
    color: var(--ql-good);
    border-color: rgba(79, 176, 174, 0.7);
    background: rgba(79, 176, 174, 0.08);
}}

.ql-badge-bad {{
    color: var(--ql-bad);
    border-color: rgba(182, 90, 92, 0.7);
    background: rgba(182, 90, 92, 0.08);
}}

.ql-note {{
    border-left: 2px solid var(--ql-gold);
    padding: 0.75rem 1rem;
    background: rgba(200, 160, 78, 0.08);
    color: var(--ql-text);
    margin: 0.8rem 0 1.1rem 0;
}}

.ql-divider {{
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin: 1.6rem 0;
}}

.ql-divider::before,
.ql-divider::after {{
    content: "";
    flex: 1;
    height: 1px;
    background: var(--ql-line);
}}

.ql-divider span {{
    color: var(--ql-gold);
    font-size: 0.7rem;
    letter-spacing: 0.18em;
}}

.ql-footer {{
    margin-top: 2.4rem;
    padding-top: 1rem;
    border-top: 1px solid var(--ql-line);
    color: var(--ql-muted);
    font-family: var(--ql-body);
    font-size: 0.78rem;
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.4rem;
}}

.ql-footer a {{
    color: var(--ql-gold-soft);
    text-decoration: none;
}}

.ql-footer a:hover {{
    text-decoration: underline;
}}

/* ---- Quality floor: focus, reduced motion, mobile ---------------------- */
:focus-visible {{
    outline: 2px solid var(--ql-gold);
    outline-offset: 2px;
}}

@media (prefers-reduced-motion: reduce) {{
    * {{
        transition: none !important;
        animation: none !important;
    }}
}}

@media (max-width: 640px) {{
    .block-container {{
        padding-top: 1.4rem;
    }}

    .ql-header {{
        align-items: flex-start;
        gap: 0.75rem;
    }}

    .ql-mark {{
        width: 2.2rem;
        height: 2.2rem;
        font-size: 1.15rem;
    }}

    .ql-title {{
        font-size: 1.6rem;
    }}

    .ql-subtitle,
    .ql-sub {{
        font-size: 0.72rem;
        letter-spacing: 0.08em;
    }}

    .ql-card {{
        min-height: auto;
    }}

    .ql-card-value {{
        font-size: 1.45rem;
    }}
}}
</style>
"""


def inject_quantlab_style() -> None:
    """Inject the Quant Lab CSS. Call once, immediately after set_page_config()."""
    st.markdown(_CSS, unsafe_allow_html=True)


def apply_quantlab_style() -> None:
    """Backward-compatible entrypoint used by main.py."""
    inject_quantlab_style()


def render_header(title: str, subtitle: str = "") -> None:
    """Render the Quant Lab header lockup."""
    sub = f'<p class="ql-subtitle">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f"""
        <div class="ql-header">
          <div class="ql-mark">⚛</div>
          <div>
            <h1 class="ql-title">{title}</h1>
            {sub}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def gold_divider(glyph: str = "◆") -> None:
    """Thin art-deco divider with a centered glyph."""
    st.markdown(f'<div class="ql-divider"><span>{glyph}</span></div>', unsafe_allow_html=True)


def render_footer() -> None:
    """Footer with the upstream MIT attribution kept visible."""
    st.markdown(
        """
        <div class="ql-footer">
          <span>Dr. Phil&#39;s Quant Lab, WSU Vietnam · for teaching use</span>
          <span>BSM engine adapted from George Dros (MIT) ·
            <a href="https://github.com/George-Dros/Black-Scholes-Interactive-heatmap"
               target="_blank" rel="noopener">source</a></span>
        </div>
        """,
        unsafe_allow_html=True,
    )
