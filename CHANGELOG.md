# Changelog

## quantlab-vn

- Forked from George Dros' MIT-licensed Black-Scholes Interactive Heatmap.
- Added the Quant Lab black-gold Streamlit theme and single CSS injection point.
- Added a data-provider layer with Yahoo Finance for US option chains, vnstock for Vietnam spot/history, manual fallback, and a FiinQuant stub for instructor credentials.
- Added a visible put-call parity badge, Greek table, formula expander, payoff chart, and dark chart styling.
- Split market logic into Vietnam spot-driven theory and US listed-option comparison because Vietnam has no exchange-listed single-stock equity options.
- Preserved the original Black-Scholes call/put pricing functions.
- Documented that `vnstock` uses a custom personal/research/non-commercial proprietary license, so commercial redistribution requires contacting vnstocks and is not covered by this repo's MIT license.
