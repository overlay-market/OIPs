---
note: 7
oip-num: 1
title: Cutting Off the Tails
status: WIP
author: Michael Feldman (@mikeyrf)
discussions-to: oip-1
created: 2021-06-12
updated: N/A
---

Issue to address with this note:

- How do we prevent payouts that would otherwise bankrupt the system? i.e. avoid becoming [Taleb's turkey](https://www.riskmanagementmonitor.com/lets-not-be-turkeys/)


## Context

<blockquote class="twitter-tweet"><p lang="tl" dir="ltr">Talib <a href="https://twitter.com/search?q=%24Titan&amp;src=ctag&amp;ref_src=twsrc%5Etfw">$Titan</a> Turkey <a href="https://t.co/6JvUjkYddn">pic.twitter.com/6JvUjkYddn</a></p>&mdash; Flood (@ThinkingUSD) <a href="https://twitter.com/ThinkingUSD/status/1405311057480929282?ref_src=twsrc%5Etfw">June 16, 2021</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>

## Mitigating the Death Spiral

Need to include:

- Payoff caps -- limits max percent change in price

- Dynamic OI caps -- limits *new* position builds when market has printed an excessive amount over a prior period of time (cooldown on trading)

Combined with payoff caps, means we can definitively calculate worst case amount system has to pay out at any moment, for a given future period of time.

Looking at prior \\( n \\) update periods to see how much printed over a rolling window. Compare with max worst case local inflation rate willing to tolerate. If larger than max inflation rate, lower OI cap to zero to prevent new positions until long enough time has passed for prior rolling window to have inflation rate below max. Then, we are setting a worst case inflation rate per market in stone instead of being solely probabilistic.

In practice, what does this look like in readjusting the inflation cap upward after cooldown period? Additionally, how should we gradually ease cap down if rate seems to be increasing over time (acceleration), so dynamic cap is somewhat smooth in readjustments?

Mitigates death spiral by:

1. Cap on contract payoff limits infinite printing from one existing set of short positions on inverse market

2. Dynamic OI cap prevents recycling of profits from capped short payout immediately into a set of *new* short positions on the inverse market to ride the price down further. Enforces a cooldown period to prevent building more positions and meet worst-case inflation expectations
