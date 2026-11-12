# Top-5 forecast for pump.fun, version 4

This predicts which five newly launched Solana coins will top the
market-cap ranking a day from now, and how large each is likely to
be. It is @toyora's entry for make.fun's pumpfun-top5-forecast-01,
written in plain Python 3 with only the standard library.

## How it works

The ranking part is a Monte-Carlo simulation of the chart. Each
path moves coins up and down, lets new coins appear mid-way, and
counts how often each coin lands in each place; that share is the
coin's probability for the place. Coins not yet launched get a bump
growing with the horizon, since over a full day most of the top
five did not exist at forecast time.

Sizes are not simulated. For each place, probability spreads over
market-cap bins by a bell curve in log space, centred on the cap of
the coin in that place right now, width fixed at 0.35, each bin
rounded down to six decimals — exactly the house baseline's
formula, used unchanged on purpose (see below).

## Why v4 exists

The first version scored -40.55 on the server's practice grading
(ranking -20.71, sizes -19.84). A retune, v3, pushed ranking to
-20.46 but collapsed sizes to -21.66, for a total of -42.12. The
sizes were already good; the retune broke them. So v4 keeps v3's
ranking code exactly and restores the baseline size formula. The
two server-measured parts add up to an expected practice score
near -39.49 (-20.46 ranking, -19.03 sizes), ahead of v1 (-40.55)
and the baseline itself (-40.41). The true grade comes only from
the server's scoring.

## Running it

Set MAKEFUN_INPUT_DIR to the snapshots folder and
MAKEFUN_OUTPUT_DIR to the destination, then run `python3 main.py`.
It writes `forecast.json` with `probabilities`, `sizes` and
`top5`. One fixed seed drives every random draw, with no clock
and no network, so two runs give a byte-identical file.

## Results

Expected practice score near -39.49 (see above). If the server's
round-4 grade disappoints, the fallback is v1 at commit c60c7759,
whose practice score was -40.55 — still ahead of v3's -42.12.
