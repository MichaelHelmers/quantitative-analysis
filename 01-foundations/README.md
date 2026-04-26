# Chapter 1 — Foundations: Prices and Returns

> **Goal of this chapter:** answer three questions.
> 1. What is quantitative analysis actually doing?
> 2. What is the single most important number we compute from a price series?
> 3. How do we get real market data into Python and turn it into that number?

A note on conventions: every domain term in this guide is defined the first time
it appears. Terms in **bold** are formally introduced; a glossary table at the end
of each chapter recaps the new vocabulary, and the repo-root [`glossary.md`](../glossary.md)
holds the running index across all chapters.

---

## 1. What is quantitative analysis?

**Quantitative ("quant") analysis** is the practice of using **data and math** to
make decisions about financial markets. Instead of asking *"is this a good
company?"* — a qualitative question — quant analysis asks measurable questions:

- "How much does this stock typically move in a day?"
- "How tightly does it follow the overall market?"
- "Has its return-per-unit-of-**risk** been better than holding cash?"

That last bullet introduces our first key term:

> **Risk** — in quantitative finance, *risk* means **uncertainty of future
> return**, not "the chance of losing money." A stock whose price reliably went
> up 1% every single day would be considered *low-risk* even though it never
> falls; a stock that swings ±5% randomly is *high-risk* even if its long-run
> average is positive. Throughout this guide, **risk** and **volatility** are
> used almost interchangeably (we define **volatility** in §4).

Almost every quant question starts from the same primitive: **prices over time**
(a **price series**), and the things we derive from it. So that's where we start.

## 2. Why we work in *returns*, not prices

A price by itself is hard to compare. A stock at $5 and a stock at $500 can move
by the same *percentage* on the same day — but their dollar moves look wildly
different.

The fix is to work in **returns** — percentage changes from one period to the
next. Returns are unitless (a "2% gain" means the same thing for any asset),
comparable across assets, and have nice statistical properties: a roughly stable
**mean** (the arithmetic average) and **variance** (a measure of spread —
formally defined in §4) over time, unlike prices, which trend.

There are two definitions you'll meet constantly:

| Name | Formula | Read as |
|------|---------|---------|
| **Simple return** | *r<sub>t</sub>* = *P<sub>t</sub>* / *P<sub>t−1</sub>* − 1 | "what your brokerage statement says" |
| **Log return**    | *r<sub>t</sub>* = ln(*P<sub>t</sub>* / *P<sub>t−1</sub>*)  | "what most quant math uses" |

where:

- *r<sub>t</sub>* — the **return** for period *t* (e.g., the return on day *t*).
- *P<sub>t</sub>* — the **price** at the close of period *t*.
- *P<sub>t−1</sub>* — the price one period earlier (the previous trading day's close, for daily data).
- *t* — a **time index** labeling each period; here, a specific trading day.
- *ln* — the **natural logarithm** (log base *e*, where *e* ≈ 2.71828).

For small daily moves the two definitions are nearly identical (math fact:
ln(1 + *r*) ≈ *r* when *r* is small). Why bother with logs? Because **log
returns add over time**: the log return of a 5-day period equals the *sum* of
the 5 daily log returns. Simple returns don't have that property — they
**compound**, meaning multi-period returns *multiply*
((1 + *r*<sub>1</sub>)(1 + *r*<sub>2</sub>)(1 + *r*<sub>3</sub>)…) rather than
add, which is messier in formulas.

We'll compute both and confirm they look the same.

<details>
<summary><b>The math, if you want it: why log returns add and simple returns multiply</b></summary>

Start from the simple-return definition rearranged:

> *P<sub>t</sub>* / *P<sub>t−1</sub>* = 1 + *r<sub>t</sub>*

The fraction (1 + *r<sub>t</sub>*) is sometimes called the **gross return** —
"$1 invested becomes (1 + *r*) dollars." Stretch over two periods using the
algebraic identity *P*<sub>2</sub> / *P*<sub>0</sub> =
(*P*<sub>2</sub> / *P*<sub>1</sub>) × (*P*<sub>1</sub> / *P*<sub>0</sub>) —
you can always insert *P*<sub>1</sub> in the numerator and denominator since
they cancel — and substitute the gross-return form:

> *P*<sub>2</sub> / *P*<sub>0</sub> = (1 + *r*<sub>1</sub>)(1 + *r*<sub>2</sub>)

So the two-period simple return is
(1 + *r*<sub>1</sub>)(1 + *r*<sub>2</sub>) − 1 =
*r*<sub>1</sub> + *r*<sub>2</sub> + *r*<sub>1</sub>·*r*<sub>2</sub>. That last
cross-term *r*<sub>1</sub>·*r*<sub>2</sub> is exactly why simple returns don't
add cleanly. **Concrete example:** −10% then +10% leaves you at
$1.00 → $0.90 → $0.99 — a two-day simple return of **−1%**, not 0%. The
cross-term (−0.10)(+0.10) = −0.01 is the missing percent.

Log returns kill the cross-term using the identity
ln(*a* · *b*) = ln(*a*) + ln(*b*):

> ln(*P*<sub>2</sub> / *P*<sub>0</sub>) = ln((*P*<sub>2</sub> / *P*<sub>1</sub>)(*P*<sub>1</sub> / *P*<sub>0</sub>)) = ln(*P*<sub>2</sub> / *P*<sub>1</sub>) + ln(*P*<sub>1</sub> / *P*<sub>0</sub>)

The two-period log return is the **sum** of the daily log returns, with no
cross-term — and the same telescoping extends to any number of periods. This
is the engine behind annualization, the reason most quant statistical models
use log returns, and why "lose 10% then gain 10%" doesn't get you back to
even.

</details>

## 3. The data we'll use

We'll pull daily data for **SPY**, the SPDR S&P 500 **ETF**.

> - **Equity** — an ownership share in a company; in everyday language, a "stock."
> - **Ticker** — the short symbol used to identify a security on an exchange
>   (e.g., `SPY`, `AAPL`, `MSFT`).
> - **Index** — a rule-based basket of securities meant to represent a market or
>   segment. The **S&P 500** is an index of the 500 largest U.S. public
>   companies, weighted by market value. An index itself isn't directly
>   tradable — it's just a number.
> - **ETF (Exchange-Traded Fund)** — a fund that holds a basket of assets and
>   *itself* trades on an exchange like a single stock. SPY is an ETF whose
>   holdings are designed to track the S&P 500 index, which is why buying one
>   share of SPY gives you economically the same exposure as owning a tiny
>   slice of all 500 companies.

So SPY is a clean, single-ticker stand-in for "the U.S. stock market." We use
one ticker now to keep things simple; in Chapter 3 we'll work with a basket.

Data source: `yfinance`, a free Python library that wraps Yahoo Finance. It's
not production-grade (rate limits, occasional gaps), but it requires no API key
and is perfect for learning.

The notebook downloads ~5 years of daily data. Each row is one **trading day**
— a day the U.S. stock market is open. There are roughly **252 trading days per
year**: 365 minus weekends (~104) and U.S. market holidays (~9). Each row
carries the **OHLCV** columns:

- **`Open`** — price at market open (9:30 ET)
- **`High`** / **`Low`** — intraday extremes
- **`Close`** — price at market close (4:00 ET), **adjusted** for splits and
  dividends by default in modern `yfinance`. This is the column we use for
  return math.
- **`Volume`** — number of shares traded that day

### Why "adjusted" matters

Suppose a stock at $100 does a 2-for-1 **split** (one share becomes two, each
worth half): now there are twice as many shares, each worth $50. The *raw*
close drops from $100 to $50 overnight — a 50% "loss" that isn't real, since a
holder now owns twice as many shares. **Adjusted close** back-propagates the
split (and any **dividends** — cash payments to shareholders) into the
historical prices so that returns reflect what an actual holder earned.
**Always use adjusted close for return calculations.**

## 4. Putting it together

The notebook walks through:

1. **Setup check** — verify the libraries import.
2. **Download** — pull 5 years of SPY data into a pandas `DataFrame`.
3. **Compute returns** — both simple and log.
4. **Visualize** — a price chart and a histogram of daily returns.
5. **Summary statistics** — mean and standard deviation of daily returns.
6. **Annualize** — convert daily numbers to yearly ones.

### A few statistical terms we lean on

We compute the **mean** and **standard deviation** of the daily-return series.
A few definitions to make those land:

> - **Mean** (μ) — the arithmetic average. Add the values, divide by the count.
> - **Variance** (σ²) — the *average squared deviation from the mean*. It
>   measures how spread out the values are. Squaring is what makes both
>   above-mean and below-mean deviations contribute positively.
> - **Standard deviation** (σ) — the square root of variance. Same units as the
>   original data (returns, in our case), which is why it's the version we
>   actually report.

We can now define the chapter's headline term:

> **Volatility** — the **standard deviation of returns**. It's our quantitative
> measure of how much an asset's price bounces around — i.e., its **risk** in
> the sense defined in §1. When you hear a trader say "vol is 20%," they mean
> the *annualized* standard deviation of returns is 0.20.

### One concept worth pre-loading: annualizing volatility

Daily numbers are awkward to talk about. Industry convention is to quote
everything on an annual basis. With ~252 trading days per year:

- **Annualized return** ≈ *mean<sub>daily</sub>* × 252
- **Annualized volatility** ≈ *std<sub>daily</sub>* × √252

where:

- *mean<sub>daily</sub>* — the mean of the daily returns (the `μ` we just computed).
- *std<sub>daily</sub>* — the standard deviation of the daily returns (the `σ`).
- *252* — the conventional number of U.S. trading days per year.
- *√252* ≈ 15.87 — the scaling factor from the √t rule below.

Why `√252` rather than `× 252` for volatility? Because *variances* (the square
of standard deviation) add over independent periods, not standard deviations
themselves. If daily returns are **i.i.d.** — *independent and identically
distributed*, meaning each day's return is drawn from the same probability
distribution and isn't influenced by other days' — then the variance of an
N-day return is N times the daily variance, so the standard deviation scales by
`√N`. (In real markets returns are *not* perfectly i.i.d. — Chapter 2 is
largely about how they fail this assumption — but i.i.d. is a useful starting
point.)

This **`√t` rule** is one of the most-used rules in quantitative finance.
Memorize it.

## 5. What you should see

When you run the notebook, expect:

- A **price chart** with a generally upward trend (the U.S. market has trended
  up over the last 5 years, with the COVID **drawdown** in March 2020 and
  **corrections** in 2022 visible).

> - **Drawdown** — the peak-to-trough decline in price, usually quoted as a
>   percent. The "max drawdown" of an asset is the worst such decline observed
>   in a window — a key risk metric we'll formalize later.
> - **Correction** — conventional name for a decline of roughly **10–20%** from
>   a recent peak. Deeper sustained declines (>20%) are called **bear
>   markets**; the opposite (sustained >20% rally) is a **bull market**. These
>   thresholds are conventions, not laws of nature.

- A **histogram** of daily returns that is bell-shaped and centered just above
  zero, with most days landing in the ±1% range and a handful of outliers in
  the ±3% to ±5% range.

> - **Distribution** — the shape that describes how often each value occurs in
>   a dataset. For a return series, the distribution tells you "what fraction
>   of days had a return near 0%, near +1%, near −2%, …".
> - **Histogram** — a chart that buckets values into ranges (*bins*) and draws
>   a bar showing how many observations fall in each bin. It's the visual shape
>   of an empirical distribution.
> - **Normal distribution (bell curve)** — the symmetric, single-peaked,
>   bell-shaped distribution. Many tools in quant finance assume returns are
>   roughly normal — a useful but imperfect approximation.
> - **Tails** — the far-left and far-right ends of a distribution, where the
>   rare large moves live. **Fat tails** means those large moves happen *more
>   often* than a normal distribution would predict — an empirical fact about
>   real returns that Chapter 2 dwells on.

- An **annualized volatility** somewhere around 15–25% — typical for a broad
  U.S. equity index. If you got a number in that range, you computed it right.

---

## Key Terms (Chapter 1)

| Term | Meaning | First used |
|------|---------|-----------:|
| Quantitative analysis | Using data and math to answer measurable questions about markets | §1 |
| Risk | Uncertainty of future return | §1 |
| Price series | Sequence of an asset's prices over time | §1 |
| Return (simple) | `Pₜ / Pₜ₋₁ − 1`; matches a brokerage statement | §2 |
| Return (log) | `ln(Pₜ / Pₜ₋₁)`; the version that adds across periods | §2 |
| Natural logarithm (`ln`) | Logarithm base *e* (≈ 2.71828) | §2 |
| Compounding | Multi-period returns multiply rather than add | §2 |
| Equity | An ownership share in a company; "stock" | §3 |
| Ticker | Short symbol identifying a security on an exchange | §3 |
| Index | Rule-based basket representing a market segment | §3 |
| S&P 500 | Index of the 500 largest U.S. public companies | §3 |
| ETF | Exchange-Traded Fund — a basket that trades like one stock | §3 |
| Trading day | A day the market is open; ~252 per year | §3 |
| OHLCV | Open / High / Low / Close / Volume — daily price columns | §3 |
| Adjusted close | Close price corrected for splits and dividends | §3 |
| Split | Re-denomination of shares (e.g., 1 → 2 of half value) | §3 |
| Dividend | Cash payment from company to shareholders | §3 |
| Mean (μ) | Arithmetic average | §4 |
| Variance (σ²) | Average squared deviation from the mean | §4 |
| Standard deviation (σ) | Square root of variance; same units as the data | §4 |
| Volatility | Standard deviation of returns; our risk metric | §4 |
| Annualizing | Rescaling per-period statistics to a yearly basis | §4 |
| √t rule | Std deviation scales by √t when periods are i.i.d. | §4 |
| i.i.d. | Independent and identically distributed | §4 |
| Distribution | Shape describing how often each value occurs | §5 |
| Histogram | Bar chart binning observations to show a distribution | §5 |
| Normal distribution | Symmetric bell-curve shape | §5 |
| Tails | Rare, extreme values at the edges of a distribution | §5 |
| Fat tails | Tails heavier than the normal distribution predicts | §5 |
| Drawdown | Peak-to-trough decline in price | §5 |
| Correction | A market decline of ~10–20% from a recent peak | §5 |
| Bear / Bull market | Sustained >20% decline / rally | §5 |

---

## Exercises

Try these in fresh cells at the bottom of the notebook:

1. **Different ticker.** Re-run the notebook with `AAPL`, `MSFT`, or `BRK-B`
   instead of `SPY`. Which has the highest annualized volatility? Why might
   that be?
2. **Different window.** Restrict to just the most recent 1 year of data and
   recompute annualized vol. Does it match the 5-year number? If not, what
   does the difference tell you?
3. **Simple vs log.** Plot simple returns and log returns on the same axes.
   Where do they start to visibly diverge?
4. **Volume.** Compute the mean of the `Volume` column and plot it over time.
   Is volume roughly stable, or does it have a trend?

---

## Up next

**Chapter 2: Risk and the not-quite-normal world.** Two questions about the
"return distribution" we computed here. *First:* does it really look like a
bell curve, or does it have heavier tails? *Second:* is its width (the
volatility) constant over time, or does it **cluster** — quiet periods
following quiet periods, stormy following stormy? Both findings are empirical
facts that drive a huge portion of modern finance, from option pricing to
risk management.
