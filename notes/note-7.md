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


For us, a death spiral can occur with OVL-X inverse markets on Overlay, where X is ETH, DAI, etc., in the scenario where all open interest on these markets is bearish OVL and a significant price drop of OVL relative to X occurs.

The payout of bearish OVL trades trends toward infinity as the price of OVL relative to X goes to zero, given the nature of the inverse market. Infinite printing by the market contract from this payout would lead to a collapse of the system.


## Stopping the Death Spiral

Building on prior caps work in [WPv1](https://firebasestorage.googleapis.com/v0/b/overlay-landing.appspot.com/o/OverlayWPv3.pdf?alt=media). To mitigate the death spiral, we can include:

- Payoff caps -- limits max percent change in price for payoff

- Dynamic OI caps -- limits *new* position builds when market has printed an excessive amount of OVL over a prior period of time (cooldown on trading)

Looking at prior \\( n \\) update periods to see how much market has printed over a rolling window. Compare with max worst case local inflation rate willing to tolerate (market param).

If larger than max inflation rate, market dynamically lowers OI cap to zero to prevent new positions from being built until long enough time has passed for window to see rolling inflation rate below max. Then, we are setting a worst case inflation rate per market in stone instead of being solely probabilistic.

In practice, what does this look like in readjusting the inflation cap upward after cooldown period? Additionally, how should we gradually ease cap down if rate seems to be increasing over time (acceleration), so dynamic cap is somewhat smooth in readjustments?

Mitigates death spiral through two layers:

1. Cap on contract payoff limits infinite printing from one existing set of short positions on inverse market. We know what is the worst case amount we can print on one "cycle" of OI builds.

2. Dynamic OI cap prevents recycling of collateral from capped short payout immediately into a set of *new* short positions on the inverse market, slowing traders ability to ride price down further after dumping prior profits -- a circuit breaker. Effectively can ensure worst case inflation rate by dynamically limiting max aggregate OI market is willing to take on for prolonged period of time.

Do we have problems if keep bumping up against max inflation rate cap and lowering caps or short circuiting trading constantly? Is this a reason for having smooth increases/decreases in dynamic cap by market contract? Or are sudden stops better?
