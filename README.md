# pumpfun-top5-forecast-01 — v4

Monte-Carlo top-5 forecaster (v4, 2026-11-12). v3's order machinery unchanged;
sizes replaced with the house baseline's exact formula (normal in log10 cap
around the current place cap, sd 0.35, floored to 6 decimals) — v3's size
calibration (0.85 MC blend, sd 0.25+0.10√h, +0.8 growth centre) scored
-21.66 on the server's dev grade vs -19.03 for the baseline's sizes, while
v3's order (-20.46) beat v1's (-20.71). Expected dev ≈ -20.46 + -19.03
= -39.49, vs v1 -40.55 and baseline -40.41.

Run: `MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 main.py`
