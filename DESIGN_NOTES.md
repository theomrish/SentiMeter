# SentiMeter — design notes

## The core separation

- We separate **surprise** and **trend move** metrics. both metrics measure different things but hide in the same numbers, so its easy to mix meanings and get confused about the direction.

- **Surprise** measure **actual**-**consensus**, it answers **were the forcasters wrong? is the situation not what they thought? by how much?**

- **Trend move**'s measure is **actual**-**prior** and tells us if the trend is alive, declining, reversing etc.

- Those are 2 metrics with 2 different meanings.

- At this point we measure first and interpret later. this is the layer that computes facts without judgement, that way when our interpretion changes the measures dont have to.

- We rewrite the opinion but keep the arithmetic

## v1 scope (Week 1)

`surprise.py` computes three facts about a scheduled economic release
and expresses no opinion about them:

| Fact | Formula | Question it answers |
|---|---|---|
| level | `actual` | where is the series now? |
| move | `actual - prior` | is it rising or falling? |
| surprise | `actual - consensus` | were forecasters wrong, and by how much? |

Worked example — CPI, prior 3.2, consensus 2.9, actual 3.0:
level 3.0 (prices still rising), move -0.2 (rising more slowly),
surprise +0.1 (slowed less than hoped). All three true at once.

## Deliberately deferred to Week 2

- **Normalisation.** A 0.1 miss on CPI and a 0.1 miss on payrolls are
  not comparable. Needs z-scoring against each series' own history.
- **Continues / halts / reverses.** The trend classification. Needs a
  threshold, which needs normalisation first.
- **Regime.** A hot CPI print does not mean the same thing in every Fed
  regime. Sometimes good news is bad news.
- **Market focus.** Attention rotates between inflation, growth and
  employment. Probably becomes a per-event-type weight that changes
  over time.
- **Risk-on / risk-off.** Needs an operational definition before it can
  be computed or graded at all.
