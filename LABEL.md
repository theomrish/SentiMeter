# Defining risk-on and risk-off

## Why this file exists

"Risk-off" started as a feeling. A feeling cannot be wrong: it adjusts itself
after the fact, every day looks like it fitted, and nothing is learned.

Week 6 scores SentiMeter by comparing its answer for a past day against the
correct answer for that day. If "correct" is a judgement made on the day of
labelling, we are measuring the labeller's mood, not the system.

So the label has to be a rule. The standard it must meet:

> Two different people, given the same day's market data and this definition,
> must independently produce the same answer.

Anything that could produce disagreement is not a definition yet.

## The label

For each completed trading day, the label is **RISK_ON** or **RISK_OFF**.
It is binary. There is no neutral class.

It is computed from three daily market series, and from nothing else.

## What goes in, and why

The starting point was the classic risk-off signature: stocks down, VIX up,
gold up, yen bid, bonds bid.

Each candidate was then put to one test:

> **Would it still have meant the same thing in 2022?**

That year matters because it was an inflation shock rather than a growth
scare, and it broke several relationships that are normally reliable.

| Component | Source | Direction | Why it survived |
|---|---|---|---|
| S&P 500 daily return | index close | down = risk-off | The most direct measure of risk appetite there is |
| VIX daily change | index close | up = risk-off | Prices the demand for protection, not just the selling |
| High-yield OAS daily change | FRED `BAMLH0A0HYM2` | wider = risk-off | Literally the price of risk: the extra yield demanded to hold junk debt instead of Treasuries |

Credit spreads are the strongest of the three, because they are not a haven
asset and therefore have no regime story of their own. They widened in 2008,
in March 2020, and in 2022 -- including through the episode that broke the
other candidates.

## What was rejected, and what killed it

**Gold.** Competes with real yields. In 2022, surging real yields hurt it even
during equity selloffs. It did not hold up.

**Bonds.** Normally the place to run. In 2022 the thing hurting stocks --
rates rising -- was the same thing hurting bonds, and they fell together.

**Yen.** Structurally a funding and haven currency, but from 2022 through 2024
the Bank of Japan held near zero while the Fed went above 5%. The carry gap
drove USDJPY from roughly 115 to 160, and that trend swamped the daily risk
signal.

None of these are bad indicators. They are **regime-dependent** indicators,
which produces the rule this whole file rests on:

> A label must mean the same thing in 2019, 2022 and 2025. Anything whose
> meaning depends on the regime belongs in the interpretation layer, not in
> the ground truth.

Gold, bonds and the yen are exactly the kind of signal the interpretation
layer should eventually weigh differently depending on the regime.

## Macro surprise is deliberately excluded

An earlier draft of this design included economic-surprise scores as about 10%
of the label. That is removed on purpose.

SentiMeter's job is: *given the day's economic releases, predict whether the
day was risk-on or risk-off.* The releases are the **input**. If they also
form part of the **answer**, then the system is handed a tenth of the answer
before it starts, and its measured accuracy in Week 6 comes out better than
its real accuracy -- invisibly.

This is called **leakage**. The label is pure market reaction: what the market
actually did. Input and answer stay strictly separate.

## The formula

For each of the three series, on day *t*:

```
z = (change_t - mean(previous 60 days' changes))
    / std(previous 60 days' changes)
```

The 60-day window **excludes day t**. Today's move must not help set the
yardstick it is measured against -- the same leak as above, in miniature.

Then, with risk-off defined as negative:

```
score = z_spx - z_vix - z_oas
```

The two minus signs invert VIX and OAS, because for those two an increase
means risk-off while for the S&P a decrease does.

```
score < 0    ->  RISK_OFF
score > 0    ->  RISK_ON
score == 0   ->  tie-break on the sign of z_spx alone
```

An exact zero across three floating-point z-scores is effectively impossible,
so the tie-break is a formality rather than a real branch.

## Numbers chosen rather than derived

Every number here that was picked rather than measured, with its honest
justification:

| Choice | Value | Justification |
|---|---|---|
| Lookback window | 60 trading days | Convention, roughly three months. Long enough for a stable estimate of typical movement, short enough to track a changing volatility regime. **Not tested.** |
| Component weights | 1 / 1 / 1 | Deliberately none. Any other weighting is a parameter that cannot be justified without evidence, and unjustified parameters are how a system gets quietly fitted to the past. Equal weights have nothing to defend. |
| Neutral band | none | Week 6 must score against this label, and three classes make that a harder evaluation. Worse, the ambiguous days are the interesting ones -- excluding them by definition would flatter the results. Whether to leave near-zero days out of the *eval set* is a separate Week 6 decision about scoring. |

## What is wrong with it

Known weaknesses, stated so that nobody -- including the author in Week 6 --
mistakes this for a finished instrument.

- **VIX is not independent of the S&P.** On a day the index falls hard, VIX
  rises almost every time. It is a correlated second opinion rather than a
  third family. Its value is in the minority of days where the two disagree.
- **HY OAS is published with a lag**, so this label can only ever be applied
  to completed days. It is unusable for anything live.
- **60 days is untested.** 30 would react faster and be noisier; 120 would be
  steadier and slower. No evidence has been gathered either way.
- **Equal weights are a starting position, not a result.**
- **US-only.** A day driven by European or Asian stress registers here only
  insofar as it reaches US markets.
- **Daily closes only.** A day that sold off hard and recovered by the close
  is scored as calm. Everything intraday is invisible.
- **No handling yet for half-days, holidays, or days when one of the three
  series does not publish.**

## Data sources

| Series | Source |
|---|---|
| S&P 500 daily close | Yahoo Finance, `^GSPC` |
| VIX daily close | Yahoo Finance, `^VIX` |
| High-yield OAS | FRED, `BAMLH0A0HYM2` |

## Related

The long-term target design lives in the risk-on / risk-off engine blueprint:
an intraday, multi-asset version with equities, volatility, an FX basket,
credit and breadth, recalculated every five minutes. That is the destination.
This file is the small, defensible starting point -- and unlike the blueprint,
every choice in it can be argued for.
