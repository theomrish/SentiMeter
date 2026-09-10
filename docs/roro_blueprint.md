# Risk-On / Risk-Off Engine — Build Blueprint

## Goal

Build a live + historical market regime engine that answers:

1. **What is the global risk state now?**
2. **Is risk appetite improving or deteriorating?**
3. **What was the final risk regime for a completed trading day?**

Do **not** use the final daily close to make intraday decisions.

---

# 1. Required Outputs

Recalculate live values every **5 minutes**.

Store:

```text
live_roro_score      # -10 to +10
live_state           # Strong Risk-Off / Risk-Off / Mixed / Risk-On / Strong Risk-On
roro_change_30m
roro_change_60m
impulse_state        # Strongly Deteriorating → Strongly Improving
confirmation_count
```

At the end of each trading day also store:

```text
final_daily_score
final_daily_label    # RISK_ON / RISK_OFF
```

Rationale: the live model is for trading context; the end-of-day model is for historical labeling and backtests.

---

# 2. Market Inputs

## Equity Risk

Use:

- ES
- NQ
- RTY

Equity basket weights:

```text
ES  = 50%
NQ  = 25%
RTY = 25%
```

Rationale: ES represents broad US risk, NQ adds growth/technology sensitivity, RTY adds small-cap/high-beta participation.

---

## Volatility

Use:

- VIX during US cash hours
- Front-month VX futures before 09:30 ET

Interpretation:

```text
VIX/VX rising  = Risk-Off
VIX/VX falling = Risk-On
```

Invert this signal in the score.

---

## FX Risk Basket

Core:

- AUDJPY
- NZDJPY
- AUDCHF
- NZDCHF

Secondary, half weight:

- CADJPY
- CADCHF

Formula:

```text
FX_raw =
(
    AUDJPY_z
    + NZDJPY_z
    + AUDCHF_z
    + NZDCHF_z
    + 0.5 * CADJPY_z
    + 0.5 * CADCHF_z
) / 5
```

Do not use USD as a core risk signal.

Rationale:

- AUD/NZD are strong cyclical/risk-sensitive currencies.
- JPY/CHF are strong safe-haven/funding currencies.
- CAD is useful but oil can distort it.
- USD is a safe haven but also strongly affected by Fed policy and rates.

---

## Credit

During US cash hours use:

```text
HYG / IEF
```

Interpretation:

```text
HYG outperforming IEF = Risk-On
IEF outperforming HYG = Risk-Off
```

For daily historical classification also use:

```text
ICE BofA US High Yield OAS
FRED: BAMLH0A0HYM2
```

Rationale: credit directly measures willingness to hold lower-quality debt versus safety.

---

## Market Participation

Use:

```text
IWM / SPY
XLY / XLP
```

Interpretation:

```text
IWM/SPY rising = small caps outperforming = Risk-On
XLY/XLP rising = discretionary outperforming staples = Risk-On
```

Breadth formula:

```text
Breadth_raw =
0.5 * IWM_SPY_z
+ 0.5 * XLY_XLP_z
```

---

# 3. Economic Data

Track:

- Core CPI m/m
- Core PCE m/m
- Nonfarm Payrolls
- Unemployment Rate
- ISM Manufacturing
- ISM Services
- Retail Sales Control Group
- Advance GDP
- Initial Jobless Claims

Required fields:

```text
timestamp
event
actual
consensus
previous
```

Use **actual vs pre-release consensus**, not actual vs previous.

Suggested surprise thresholds:

| Event | Threshold | Risk-Friendly Direction |
|---|---:|---|
| NFP | 50k | higher |
| Unemployment | 0.1 pp | lower |
| ISM Manufacturing | 1.0 | higher |
| ISM Services | 1.0 | higher |
| Retail Sales Control | 0.3 pp | higher |
| GDP | 0.5 pp | higher |
| Initial Claims | 15k | lower |
| Core CPI m/m | 0.1 pp | lower |
| Core PCE m/m | 0.1 pp | lower |

Calculate:

```text
surprise =
direction * (actual - consensus) / threshold
```

Where:

```text
direction = +1 if higher is risk-friendly
direction = -1 if lower is risk-friendly
```

Clamp surprise to:

```text
[-1, +1]
```

Live macro contribution decays after release:

```text
0–30m   = 100%
30–60m  = 75%
1–2h    = 50%
2–4h    = 25%
4h+     = 0%
```

Rationale: economic data matters through its market implication. Price action should dominate the final classification.

---

# 4. Normalize Every Market Input

Do not compare raw percentage moves between assets.

For each asset at time `t`:

```text
return_t = ln(price_t / previous_session_close)
```

Then calculate a same-time historical z-score:

```text
z_t =
return_t
/
std(
    previous 60 sessions'
    previous-close-to-same-time returns
)
```

Example:

At 10:15 ET, compare today's previous-close-to-10:15 move against the previous 60 sessions' moves measured at 10:15 ET.

Use only data available before the current observation. No lookahead.

Then clamp:

```text
z = clip(z, -1, +1)
```

Examples:

```text
+1.7σ -> +1.0
+0.4σ -> +0.4
-0.8σ -> -0.8
-2.2σ -> -1.0
```

Rationale: same-time normalization handles intraday volatility patterns; clipping prevents one extreme market from dominating the engine.

---

# 5. Live Component Scores

## Equity

```text
equity =
clip(
    0.50 * ES_z
    + 0.25 * NQ_z
    + 0.25 * RTY_z,
    -1,
    +1
)
```

Weight in final model:

```text
3.0
```

---

## Volatility

```text
volatility =
-clip(VIX_or_VX_z, -1, +1)
```

Weight:

```text
2.0
```

---

## FX

```text
fx =
clip(
    (
        AUDJPY_z
        + NZDJPY_z
        + AUDCHF_z
        + NZDCHF_z
        + 0.5 * CADJPY_z
        + 0.5 * CADCHF_z
    ) / 5,
    -1,
    +1
)
```

Weight:

```text
2.0
```

---

## Credit

```text
credit =
clip(HYG_IEF_z, -1, +1)
```

Weight:

```text
1.5
```

Only available when HYG and IEF are trading.

---

## Breadth

```text
breadth =
clip(
    0.5 * IWM_SPY_z
    + 0.5 * XLY_XLP_z,
    -1,
    +1
)
```

Weight:

```text
1.0
```

Only available during US cash hours.

---

## Macro

```text
macro = weighted active macro surprise score
```

Clamp:

```text
[-1, +1]
```

Weight:

```text
0.5
```

---

# 6. Live RORO Formula

```text
raw_live_roro =
3.0 * equity
+ 2.0 * volatility
+ 2.0 * fx
+ 1.5 * credit
+ 1.0 * breadth
+ 0.5 * macro
```

Maximum full-data range:

```text
-10 to +10
```

---

# 7. Missing-Data Rule

Before US cash open, credit and breadth may be unavailable.

Never silently treat missing data as neutral.

Calculate:

```text
available_weight =
sum(weights of components with valid data)
```

Require:

```text
available_weight >= 5.0
```

Otherwise return:

```text
INSUFFICIENT_DATA
```

If enough data exists, rescale:

```text
live_roro =
raw_live_roro * (10 / available_weight)
```

Clamp final score:

```text
[-10, +10]
```

---

# 8. Live State Thresholds

```text
score >= +5      STRONG_RISK_ON
+2 <= score < +5 RISK_ON
-2 < score < +2  MIXED
-5 < score <= -2 RISK_OFF
score <= -5      STRONG_RISK_OFF
```

Do not force weak positive/negative readings into Risk-On or Risk-Off. `MIXED` is a valid state.

---

# 9. Risk Impulse

State tells where the market is.

Impulse tells where it is going.

Calculate:

```text
delta_30m = live_roro_now - live_roro_30m_ago
delta_60m = live_roro_now - live_roro_60m_ago
```

Classify each:

```text
delta >= +3       STRONGLY_IMPROVING
+1 to +3          IMPROVING
-1 to +1          STABLE
-3 to -1          DETERIORATING
delta <= -3       STRONGLY_DETERIORATING
```

Example:

```text
State:   RISK_OFF (-3.1)
Impulse: STRONGLY_IMPROVING (+4.4 / 60m)
```

This means the market remains risk-off but risk pressure is rapidly reversing.

---

# 10. Confirmation Rule

Major signal families:

1. Equity
2. Volatility
3. FX
4. Credit
5. Breadth

For each family:

```text
component > +0.25 -> confirms Risk-On
component < -0.25 -> confirms Risk-Off
otherwise         -> neutral
```

For `STRONG_RISK_ON` or `STRONG_RISK_OFF`, require at least:

```text
3 of 5 families
```

to agree with the score direction.

If the numerical score is strong but fewer than 3 families agree, downgrade to:

```text
RISK_ON_LOW_CONFIRMATION
```

or:

```text
RISK_OFF_LOW_CONFIRMATION
```

Rationale: one asset family should not be able to create a false global regime.

---

# 11. Divergence Flags

Create explicit diagnostic flags.

## Rally Not Confirmed

Trigger when:

```text
NQ/ES rising strongly
AND
at least 3 of:
    FX < -0.25
    Credit < -0.25
    Breadth < -0.25
    Volatility < -0.25
```

Return:

```text
RISK_RALLY_NOT_CONFIRMED
```

## Selloff Pressure Dissipating

Trigger when:

```text
NQ/ES near session lows
AND
live_roro improved by >= 3 points over 30–60 minutes
```

Return:

```text
RISK_OFF_PRESSURE_DISSIPATING
```

These are context flags, not direct trade signals.

---

# 12. Historical Daily Classifier

Build separately from the live engine.

Suggested daily weights:

```text
SPX return             20.00%
VIX change             20.00%
HY OAS change          15.00%
HYG/IEF                  7.50%
IWM/SPY                  3.75%
XLY/XLP                  3.75%
FX basket               20.00%
Macro surprise          10.00%
```

Normalize daily market moves using trailing 60-session volatility, excluding the current day.

Invert VIX and HY OAS because increases are Risk-Off.

Calculate:

```text
daily_score
```

Then force a binary label:

```text
daily_score > 0 -> RISK_ON
daily_score < 0 -> RISK_OFF
```

If exactly zero:

1. Use the sign of the core score: SPX + VIX + HY OAS + FX.
2. If still zero, use SPX daily return.

Purpose: create reproducible historical labels for research. Never use the final label before the day is finished.

---

# 13. Data to Persist

For every live timestamp save:

```text
timestamp

ES_z
NQ_z
RTY_z
VIX_VX_z

AUDJPY_z
NZDJPY_z
AUDCHF_z
NZDCHF_z
CADJPY_z
CADCHF_z

HYG_IEF_z
IWM_SPY_z
XLY_XLP_z

macro_score

equity_score
volatility_score
fx_score
credit_score
breadth_score

live_roro_score
live_state

delta_30m
delta_60m
impulse_state

confirmation_count
divergence_flags
available_weight
```

Do not store only the final score. Component history is required for debugging and future research.

---

# 14. Development Order

## V1 — Core Live Engine

Implement:

- ES
- NQ
- RTY
- VIX/VX
- AUDJPY
- NZDJPY
- AUDCHF
- NZDCHF

Build:

- data ingestion
- previous-close returns
- same-time 60-day normalization
- Equity score
- Volatility score
- FX score
- Live RORO
- 30m/60m impulse

Do not continue until historical and live calculations are reproducible.

---

## V2 — Confirmation Layer

Add:

- HYG/IEF
- IWM/SPY
- XLY/XLP

Build:

- Credit score
- Breadth score
- confirmation count
- low-confirmation states
- divergence flags

---

## V3 — Macro Layer

Add economic calendar data.

Build:

- actual vs consensus surprise calculation
- event thresholds
- release weights
- time decay

Keep macro contribution small.

---

## V4 — Historical Research Engine

Generate several years of:

- intraday RORO series
- final daily scores
- daily Risk-On/Risk-Off labels
- component scores

Validate manually against known stress, relief-rally, and calm sessions.

---

# 15. Research After the Engine Works

Do not assume `Risk-On = buy NQ`.

Test conditional behavior.

Examples:

```text
NQ forward return by Live RORO bucket
NQ forward return by 30m/60m RORO impulse
NQ behavior when RORO crosses -2 -> +2
NQ behavior during price/RORO divergences
Gold behavior by RORO state
Gold behavior when USD/rates disagree with broad RORO
Setup expectancy conditional on RORO state
```

The engine's job is to describe the environment.

The trading model should answer:

```text
Given:
- my setup
- current RORO state
- RORO impulse
- time of day
- confirmation/divergence

does this setup have positive historical expectancy?
```

---

# 16. Non-Negotiable Rules

1. **No lookahead.**
2. Use only data that was available at the timestamp being evaluated.
3. Use previous session close as the live reference.
4. Normalize intraday moves against the same timestamp over the previous 60 sessions.
5. Clamp normalized inputs to `[-1, +1]`.
6. Never treat missing data as neutral.
7. Keep live and final-daily classifiers separate.
8. Preserve every component for auditing.
9. Macro never overrides broad cross-asset price behavior by itself.
10. RORO is market context, not a direct entry signal.
