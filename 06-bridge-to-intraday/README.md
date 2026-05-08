# Chapter 6 — Bridge: From Daily Bars to Intraday Data

Chapters 1–5 lived entirely in daily-bar space. Every chapter from this point forward operates intraday: minute bars, sub-session holding periods, regime context that varies *within* a single trading day. This chapter crosses that boundary cleanly, so subsequent chapters can assume you have working intraday data, know how time-of-day shapes returns, and understand how minute bars differ from daily bars in structurally important ways.

It is the first chapter that's not about *measurement* — it's about practice. There is almost no new statistical machinery; the math budget is intentionally near-zero. The work is in tooling, intuition, and one or two pictures that are pedagogically irreversible — once you've seen the U-shape, you can never go back to thinking returns are i.i.d. across a session.

## Three things change going from daily to intraday

1. **Time has a clock.** Returns are not exchangeable across the session. A 9:32 ET return is drawn from a different distribution than a 12:04 ET return. Vol per minute follows a roughly U-shaped pattern across the day. (§4.)
2. **The bar isn't given to you.** On daily timeframes the close is a natural sampling boundary — the market shuts at 4 PM and reopens at 9:30 AM. Intraday, *you* choose how to slice the data: every minute, every fixed number of shares, every fixed dollar volume, every unit of order-flow imbalance. Different choices, different statistical properties. (§3.)
3. **External events punch through the seasonality.** At 14:00 ET on a scheduled FOMC announcement day, vol jumps several-fold regardless of where in the U-shape you are. Same for CPI prints (8:30 ET pre-market) and Non-Farm Payrolls (8:30 ET pre-market). (§5.)

Each of those is one section of this chapter.

## §1 — Why intraday data is different

Chapter 1 said i.i.d. returns are an idealization the rest of the curriculum keeps pushing back on. Daily-bar returns aren't i.i.d. — Chapter 2 showed vol clustering and fat tails. Intraday data violates i.i.d. in a *different* way that's easier to see and harder to unsee: returns are not exchangeable across the session, because time itself has structure. The 9:32 ET minute is a different beast from the 12:04 ET minute.

Every measurement we built in Chapters 1-5 — vol, VaR, Sharpe — assumed a return distribution that was at least *stationary in time*. That assumption gets ripped up here. Going forward, "stationary" needs a session-time qualifier.

## §2 — Where the data comes from: Alpaca free-tier setup

Daily SPY bars from Yahoo Finance got us through Chapters 1–5 because they're free, no signup, and a lifetime of history is one HTTP request away. Intraday data is harder. Free vendors with multi-year minute-bar history are scarce; most charge.

This curriculum uses **Alpaca Markets** (https://alpaca.markets) free tier. Alpaca is a US brokerage with a Trading API; opening a *paper-trading* account is free, takes a few minutes, and gives you bundled access to historical IEX-feed minute bars with multi-year depth. We never place a real trade in this curriculum until Ch18; the paper account is just a credentialed gateway to data.

> **Two Alpaca products — pick the right one.** Alpaca offers a **Trading API** (for individual traders) and a **Broker API** (for businesses building a brokerage app on Alpaca's infrastructure). You want the Trading API. The Market Data API is bundled with it, no separate signup needed.

> **Non-US-resident note.** Alpaca account creation may not be available in all jurisdictions. If you can't sign up, the chapter is still valuable for the conceptual content; for hands-on, the same code works against any minute-bar source you can substitute (Polygon free tier, Databento community sample, archived broker tape) — only the data-loading function changes.

### Setup steps

1. Sign up at https://alpaca.markets and verify the account.
2. From the dashboard, generate **paper-trading** API keys. You'll get an `APCA_API_KEY_ID` (~26 chars) and an `APCA_API_SECRET_KEY` (~44 chars).
3. Copy `.env.example` from the repo root to `.env` and paste your keys:
   ```
   APCA_API_KEY_ID=PKxxxxxxxxxxxxxxxxxx
   APCA_API_SECRET_KEY=yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
   ```
   `.env` is listed in `.gitignore`. **Never commit it.**
4. Install the SDK and parquet engine — already in `requirements.txt`:
   ```bash
   uv pip install -r requirements.txt
   ```
   New for this chapter: `alpaca-py`, `pyarrow`, `python-dotenv`.

### The pull script

Pull one year of 1-minute bars for QQQ (primary) and SPY (Exercise 1) and cache them locally as parquet. The cache is in `06-bridge-to-intraday/data/`, gitignored — re-fetch any time. Save the script as `pull_data.py` in the chapter folder, or just paste into a shell:

```python
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

load_dotenv()
client = StockHistoricalDataClient(
    os.environ["APCA_API_KEY_ID"], os.environ["APCA_API_SECRET_KEY"]
)
end = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
start = end - timedelta(days=365)

DATA = Path("data")
DATA.mkdir(exist_ok=True)

for sym in ["QQQ", "SPY"]:
    req = StockBarsRequest(
        symbol_or_symbols=[sym],
        timeframe=TimeFrame.Minute,
        start=start,
        end=end,
        feed="iex",
    )
    bars = client.get_stock_bars(req).df
    bars = bars.reset_index(level=0, drop=True)
    bars.index.name = "ts_utc"
    bars.to_parquet(DATA / f"{sym.lower()}_1min.parquet")
    print(f"{sym}: {len(bars):,} rows")
```

> The `data/` directory is gitignored repo-wide, so a fresh clone won't have it. The script creates the folder on first run via `DATA.mkdir(exist_ok=True)`. Subsequent runs reuse the cache.

Expected output: ~100k rows per symbol over a year (24h-coverage bars; we filter to RTH later). Two parquet files in `data/`, ~5 MB each.

### Why we cache locally as parquet

Three reasons:

1. **Iteration speed.** The notebook re-runs in seconds against a parquet read, vs minutes against a fresh API call. You'll edit and re-run the notebook many times.
2. **Reproducibility.** Alpaca's IEX feed *can* change — backfill corrections happen. Snapshot once, work against the snapshot, refresh deliberately.
3. **Rate limits.** Free tier has them; if you re-pull every notebook run you'll hit caps quickly during a working session.

Parquet (via `pyarrow`) is the format of choice for time-series like this — columnar, compressed, with type fidelity for the timestamp index.

## §3 — Bar construction: time, volume, dollar, imbalance

The 1-minute bars from Alpaca are **time bars** — every minute of wall-clock time, regardless of how much trading happened in it. Time bars are the workhorse of this curriculum (and most quant work) because they're regular, easy to reason about, and natively supported by every backtest library. But they're not the only choice — and on intraday timeframes the alternatives matter enough to know about.

The four bar types you'll see in the literature, ordered by how widely they're used:

- **Time bars** (this curriculum's default): every N minutes/seconds. Regular cadence, but information density varies wildly across the day — a 1-minute bar at 9:31 ET represents very different amounts of trading than a 1-minute bar at 12:31.
- **Volume bars**: every N shares traded. Equalizes information density by share count.
- **Dollar bars**: every $N of notional traded. Equalizes further (handles price changes over time, so a bar from 2010 and a bar from 2026 represent comparable amounts of *capital* changing hands).
- **Imbalance bars**: every N units of signed order-flow imbalance (buys minus sells). Equalizes by *information arrival* in a microstructural sense. Most exotic; needs trade-direction inference (Lee-Ready or similar) when the data only tells you "a trade happened" without saying buyer- or seller-initiated.

In §6 of the notebook we build dollar bars for one trading day on QQQ and compare bar-counts-per-hour against the constant 60-per-hour you'd get from minute bars. Time bars give you the same number per hour by construction; dollar bars cluster where the activity is — relatively few during midday, *many* at the close.

This curriculum uses time bars exclusively through Ch15. Dollar bars resurface in Ch13 (microstructure & execution) when slippage modeling needs information-equalized samples. Volume bars and imbalance bars are named here only — for the canonical treatment, see López de Prado, *Advances in Financial Machine Learning* (Wiley, 2018), Chapter 2.

## §4 — Intraday seasonality: the U-shape

The chapter's empirical hook. For each minute of the trading session — minute 0 = 9:30 ET, minute 389 = 15:59 ET — compute the mean absolute log return across all sessions in the data window, then plot. The notebook does this in two cells (one to compute, one to plot).

The numbers you should see on QQQ for a one-year window:

| Window | Mean \|return\| | Ratio to midday |
|---|---|---|
| Open: minutes 1–5 (9:31–9:35) | ~5.96 bp | 2.27× |
| Midday: minutes 180–184 (12:30–12:34) | ~2.63 bp | 1.00× |
| Close: minutes 385–389 (15:55–15:59) | ~3.08 bp | 1.17× |

(*bp = basis points = 0.01% per minute. Numbers will shift if you re-pull a different window.*)

**What this picture says — and what it doesn't.** The textbook story you'll read in older microstructure papers is that intraday vol is U-shaped: high at the open, calm through midday, *high* at the close. On QQQ in this window, the morning peak is real and clean — about 2.27× the midday baseline — but **the closing bump is barely there in vol terms** (1.17× midday). It's there if you squint, but it's not the dramatic second peak the textbook story promises.

This is where being honest with the data matters. Two possibilities:

1. The classic U-shape was strongest when most trading happened on a single venue (NYSE floor) and intraday infrastructure was different. Modern markets fragment trading across many venues with different intraday rhythms; the aggregate "U" smooths out.
2. The closing burst lives in *activity* (volume, dollar volume) rather than in *return magnitude*. We'll see this clearly in §6 — closing-hour dollar volume is much higher than midday — even though the closing returns themselves aren't dramatically larger than midday returns.

Both are true. The second is the more useful framing for an intraday trader: **vol per return ≠ amount of trading**, and they don't always move together. Strategies that need *liquidity* (large-size execution, thin-spread fills) care about activity. Strategies that need *vol* (mean-reversion thresholds, breakout filters) care about return magnitude. Don't conflate them.

**Decision rule unlocked.** Any strategy that doesn't condition on time-of-day implicitly assumes stationarity that is empirically wrong by 2-3× across a session on QQQ. Sizing thresholds, stop losses, signal-significance tests — all need a session-time component, or they're mis-calibrated. A "1% move" at 9:32 means something very different from a "1% move" at 12:32, even though they're both 1%.

## §5 — Event windows preview

The U-shape isn't the whole story. Some sessions have *additional* structure on top of seasonality, driven by scheduled releases that the entire market knows are coming.

Three to know:

- **FOMC announcements.** The Federal Open Market Committee sets the federal-funds-rate target. Eight scheduled meetings per year, with the press-release announcement at **14:00 ET** (followed by a press conference at 14:30 on alternating meetings). Vol around the announcement minute jumps several-fold.
- **CPI release.** Consumer Price Index — the headline inflation print. Released monthly by the BLS at **08:30 ET**, in the pre-market session. The 8:30 minute and the 9:30 cash open absorb the bulk of the reaction.
- **NFP / Employment Situation.** Non-Farm Payrolls — the headline labor-market print. Also monthly, also 08:30 ET pre-market. Same general pattern as CPI.

The notebook §5 hardcodes the eight FOMC dates that fell in the data window, builds two U-shapes (FOMC days vs all other days), and overlays them. The FOMC line tracks the non-FOMC line through the morning, then explodes at minute 270 (14:00 ET). The headline number on this window:

> **At 14:00 ET on FOMC days, mean |return| is ~12.23 bp vs ~2.73 bp on non-FOMC days — a 4.49× ratio.**

Pedagogically, the takeaway is simple: **the U-shape isn't a complete model of intraday vol.** The day's calendar punches holes through it.

**Forward pointer.** Building strategies around scheduled events is its own subject, but the toolkit lives in two later chapters:
- **Ch15** (intraday vol & regime detection) — how to detect that you've entered a high-vol regime, how to vol-target through it, when to flat-line.
- **Ch16** (more strategies) — an event-driven strategy as one of the worked examples.

Ch6's job is just: see that the spike exists.

## §6 — Bar gaps and short sessions

Real intraday data has gaps. Some are legitimate (no trades happened on IEX in that minute); some are vendor issues; some reflect short trading sessions (early closes around holidays). Audit before you trust.

The notebook §7 runs three quick checks on the QQQ RTH window:

1. **Bars present with `volume == 0`.** Effectively zero — if a bar exists, it has a trade in it.
2. **Sessions with fewer than the expected 390 RTH bars.** **172 out of 251 sessions** — most of them. Average ~380 of 390 bars per session.
3. **List of the very-short sessions.** Sorted by length; the genuinely short ones are likely real holiday early closes.

That second number is striking and worth dwelling on. Why are most sessions missing some bars?

**The answer is the IEX-feed structure.** IEX (Investors Exchange) is one stock exchange among many in the US National Market System. The Alpaca free tier streams IEX trades — minute bars are constructed from trades that printed *on IEX*. If a minute had trades on NASDAQ or NYSE but none on IEX, that minute produces no bar in the IEX feed. You see this most often in midday minutes when overall activity is light and IEX (a smaller venue) might miss the print entirely.

This is what an IEX-only feed looks like: not "data outage," but "IEX-as-a-sample-of-all-trading." The full consolidated tape (SIP) would have ~390 bars per session almost every day. The free-tier IEX feed has gaps, and those gaps are pervasive.

**Practical implication for everything that follows.** When you join intraday bars to a session-time index (e.g., for the §4 U-shape), you'll get NaNs scattered through the data. You have two reasonable choices:

1. **Reindex to the full minute grid and forward-fill price.** Treats gaps as "no change" and gives you a 390-bar-per-session table. Useful when downstream code expects regular spacing.
2. **Leave the gaps and aggregate over only the bars you have** (groupby preserves NaNs). Gives honest counts at the cost of needing care when computing rolling statistics.

This curriculum mostly uses option 2 — pandas `groupby` and `dropna` handle it cleanly, and "average over the minutes that printed" is a defensible aggregator. We'll flag where option 1 matters specifically.

What's *not* defensible is silently treating the gappy data as if every session has 390 bars. That's the kind of bug a backtest harness can hide for months.

### RTH vs ETH (regular vs extended trading hours)

For QQQ, **RTH** (Regular Trading Hours) is **9:30 AM – 4:00 PM ET**, Monday through Friday. The 6.5-hour cash session.

**ETH** (Extended Trading Hours) covers pre-market (~4:00 AM – 9:30 AM ET) and after-hours (~4:00 PM – 8:00 PM ET). ETH exists for QQQ but is much thinner — wider spreads, gappy prints, less reliable for systematic strategies. Alpaca returned ETH bars in the pull script but we filtered them out in §3 of the notebook. Most of this curriculum operates RTH-only; sub-session strategies rarely benefit from holding through pre-market or after-hours given the liquidity penalty.

### Holidays and early closes

The NYSE/NASDAQ session calendar isn't a clean 252-day annual rhythm. Roughly nine full holiday closures per year (New Year's Day, MLK Day, Presidents Day, Good Friday, Memorial Day, Juneteenth, Independence Day, Labor Day, Thanksgiving, Christmas) and ~3 partial-day closures (the day after Thanksgiving, July 3rd if July 4th falls on a Saturday, December 24th — early closes at 1:00 PM ET).

Always check the official calendar at https://www.nyse.com/markets/hours-calendars before declaring a session "abnormally short." A 210-bar session might be a real 1:00 PM early close, not a data outage.

### Futures vs equity sessions

A brief gloss to set up Ch17. Futures trade nearly 24-hours electronically (CME has a brief daily maintenance window, typically 17:00 – 18:00 ET on weekdays plus weekend closure). There's no "RTH vs ETH" split for NQ in the same way — there's just the continuous session and a few high-activity windows around the cash equity open and close. We'll cover this fully in **Ch17 — Futures mechanics & NQ specifics** when the curriculum graduates from QQQ to NQ.

## §7 — So what?

Decision rules this chapter unlocks:

- **Vol estimates, signal thresholds, and stop-losses must condition on time-of-session.** A fixed threshold is mis-calibrated by ~2-3× across the day on QQQ. Even a simple "scale by minute-of-session vol" pre-processing step is a meaningful improvement.
- **Vol is not the same as activity.** The closing hour is huge in dollar volume but only mildly elevated in return magnitude. Liquidity-sensitive strategies (large size, tight spreads) care about the first; threshold-sensitive strategies (mean-reversion, breakout) care about the second.
- **Around scheduled events (FOMC, CPI, NFP), vol jumps to a different regime.** Either model the regime (Ch15) or flat-line through it. A strategy that ignores the calendar will look great on average and catch fire on FOMC days.
- **Always cache minute data locally.** Reprocessing latency kills iteration speed; you'll be re-running the notebook many times.
- **Audit the data for gaps and short sessions before trusting it.** Bad assumptions about session length cause silent backtest bugs. On the IEX feed specifically, expect ~2-3% of bars to be missing from a typical session.

What this chapter can't yet tell you:

- **How to build a tradable signal from intraday data.** That's Ch7 (strategy taxonomy — where do edges come from?) and Ch8 (your first runnable mean-reversion strategy on QQQ).
- **Whether a strategy's edge is real or a statistical artifact.** That's the Ch9–11 backtesting trio.
- **How to size a position given that vol moves intraday.** That's Ch14 (Kelly + risk-of-ruin) and Ch15 (intraday vol & regime detection).
- **How NQ futures differ from QQQ.** That's Ch17 (futures mechanics & NQ specifics).

## Key Terms

| Term | Definition |
|---|---|
| RTH (Regular Trading Hours) | 9:30 AM – 4:00 PM ET, Mon–Fri. The main equity cash session. |
| ETH (Extended Trading Hours) | Pre-market (~4:00–9:30 ET) and after-hours (~16:00–20:00 ET). Thin liquidity, wider spreads. |
| Time bar | A bar covering a fixed wall-clock interval (e.g. 1 minute). Constant cadence, varying information density. |
| Volume bar | A bar covering a fixed share-count of trading. Equalizes information density by share count. |
| Dollar bar | A bar covering a fixed notional ($) of trading. Equalizes information density by capital changing hands. |
| Imbalance bar | A bar covering a fixed signed-order-flow imbalance. López de Prado, *Advances in Financial Machine Learning*. |
| FOMC | Federal Open Market Committee — sets the US federal-funds-rate target. ~8 announcements/year at 14:00 ET. |
| CPI | Consumer Price Index — monthly inflation print at 08:30 ET. |
| NFP | Non-Farm Payrolls — monthly employment print at 08:30 ET. |
| U-shape | Intraday pattern where mean abs return is high at the open, low midday, and elevated (sometimes high, sometimes mild) into the close. |
| Intraday seasonality | Time-of-day structure in any session-stationary statistic (vol, volume, spread). |
| Session boundary | Transition between session N's close and session N+1's open. For sub-session strategies, mostly "ignore." |
| Bar gap (intraday) | A minute with no IEX print (legitimate IEX-feed gap) or no data (vendor issue). |
| IEX feed | Trades that printed specifically on IEX (Investors Exchange). Free-tier Alpaca data. Subset of total US trading. |
| SIP | Securities Information Processor — the consolidated full-tape feed. Paid upgrade. |

## Up next

**Chapter 7 — Strategy taxonomy: where edges come from.** Now that we have a working intraday data substrate, the next conceptual question is: *what makes a strategy work*? We'll frame the four families — mean reversion, momentum, breakout, event-driven — by their **edge mechanism**. Every viable strategy needs to answer "where does the edge come from?" with something better than a backtest.

After that, **Ch8** is your first runnable mean-reversion strategy on QQQ, end-to-end: idea → signal → naive backtest → first look at results. From there it's three chapters of backtest discipline, then execution realism, sizing, regime detection, more strategies, futures mechanics, and going live.

## Exercises

1. **SPY vs QQQ U-shape comparison.**

   Load `data/spy_1min.parquet` (cached alongside QQQ from the §2 pull script), apply the same RTH filter and minute-of-session aggregation as §4, and overlay both U-shapes on the same axes.

   Questions to answer in a paragraph:
   - Same shape? Same magnitude?
   - Where do they diverge? (Hint: tech-heavy QQQ vs broader-market SPY have different vol and different sector mixes.)
   - Does one have a stronger closing burst than the other?

2. **Dollar bars on a stress day.**

   Pick one of the eight FOMC announcement dates from §5. Build dollar bars for that day at the same threshold you used for the §6 quiet day (or recompute with the day's own total). Plot bars-per-hour and compare to the §6 quiet-day plot.

   Questions:
   - Where in the day do dollar bars accelerate?
   - Does that match where you'd expect news-driven trading to cluster?
   - What's the dollar-bar count in the 14:00 hour specifically?

3. **CPI release seasonality.**

   CPI is released monthly at 08:30 ET in pre-market. Find the CPI release dates in the data window from the BLS calendar (https://www.bls.gov/schedule/news_release/cpi.htm) and hardcode them like the FOMC list. Re-filter your data to *include* pre-market (e.g., minute_of_day in `[4*60, 9*60+30]` for ETH plus your existing RTH range), aggregate vol per minute on CPI days vs non-CPI days, and check:

   - Does the spike land at 8:30 in pre-market?
   - Does it roll into the 9:30 cash open?
   - Is it as sharp as the FOMC 14:00 spike?

4. **Bar-gap audit on a problem session.**

   From the §7 short-session list, pick one session with significantly fewer than 390 bars (say, < 360). Cross-reference to the official NYSE/NASDAQ calendar — was it a real holiday early close (1:00 PM ET)? A vendor-side outage on IEX? A normal day with an unusually quiet midday on IEX specifically?

   Write a one-paragraph diagnostic: what happened, how would your strategy code need to handle it, and is this an everyday occurrence or a rare edge case?
