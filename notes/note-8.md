---
note: 8
oip-num: 1
title: Bid-Ask Spread
status: WIP
author: Adam Kay (@mcillkay), Michael Feldman (@mikeyrf), James Foley (@realisation)
discussions-to: oip-1
created: 2021-08-03
updated: N/A
---

Issue to address with this note:

- Prevent traders from taking advantage of the fact that the TWAP is a lagging indicator of the spot price.


## Context

Offering Uniswap TWAPs as markets on Overlay comes with a catch. The TWAP averaged over the previous \\( \Delta \\) blocks only catches up to changes in the spot price *after the next* \\( \Delta \\) blocks have gone by. This is easily exploitable as a trader, particularly on large jumps in spot.

A trader could wait for a jump to happen on the spot market, realize the direction the TWAP will be going once it catches up to spot over the next \\( \Delta \\) blocks, and scalp an easily assured profit. We've already seen this on [Kovan](https://kovan.overlay.exchange/) with our old contracts.

For example,

![Image of Twap Lag Plot](../assets/oip-1/twap_lag.png)

displaying 1.5 hours of [simulated data](https://github.com/overlay-market/pystable/blob/main/example/montecarlo.py) generated from fits to ETH-DAI historical price data. The TWAP is averaged over an hour.

The 1h TWAP value immediately after spot jumps from 1983.65 to 1995.48 is still around 1985.86, and the 1h TWAP value an hour after the jump catches up is 2002.48. If we offer the long entry and exit prices at the rolling 1h TWAP value, the scalp trade over an hour yields easy money.


## Responsive Spreads

To prevent traders from taking advantage of the lag, one solution is to add a "bid-ask spread" to the entry and exit values Overlay markets offer to traders. Such a spread should be responsive to large jumps in the most recent spot price while also inheriting the security properties of the TWAP when traders wish to ultimately take profits.

We propose the bid \\( B(t) \\) and ask \\( A(t) \\) prices offered to traders at time \\( t \\) be

\\[ B(t) = \min \bigg[\mathrm{TWAP}(t-\nu, t), \mathrm{TWAP}(t-\Delta, t) \bigg] \cdot e^{-S} \\]

\\[ A(t) = \max \bigg[\mathrm{TWAP}(t-\nu, t), \mathrm{TWAP}(t-\Delta, t) \bigg] \cdot e^{S}  \\]

where \\( \nu \ll \Delta \\).

Longs receive the ask as their entry price and the bid as their exit price. Shorts receive the bid as their entry price and the ask as their exit price.

\\( \mathrm{TWAP}(t-\nu, t) \\) is a shorter TWAP used as a proxy for the most recent spot price. Traders unfortunately receive the worst possible price, but it does protect the system both against the predictability of the lag in the longer TWAP *and* [spot price manipulation](#spot-manipulation). Good starting values to average over would be \\( \nu = 40 \\) for a 10m shorter TWAP and \\( \Delta = 240 \\) for a 1h longer TWAP.

\\( S \\) is an additional static spread, on top of the bid-ask TWAP values, used to discourage front-running of the shorter TWAP, which acts as a proxy for spot. Spot values from Uniswap pools shouldn't be used, as they [are vulnerable to manipulation](https://samczsun.com/taking-undercollateralized-loans-for-fun-and-for-profit/).

Applying a spread with \\( S = 0.00624957 \\) to the 1.5 hours of simulated data plotted above

![Image of Twap Lag With Spread Plot](../assets/oip-1/twap_lag_double_spread.png)

shows the scalp is no longer profitable over the hour following the jump, as the same long trade now has an entry price at the ask of 1998.31, immediately after the jump, and an exit price at the bid of 1990.01, 1 hour after the jump.

The downside with this approach is we likely reduce the amount of higher frequency trading that occurs on the platform. Over shorter time horizons, it becomes more difficult to exit with a profit, as one has to overcome the spread. For example, examining 6 hours of simulated data

![Image of Twap Lag With Spread And Vol Plot](../assets/oip-1/twap_lag_double_spread_vol.png)

shorting the local top here gives an entry price at the bid of 2489.67 and an exit price at the ask of 2459.50, for a profit (without fees) of 1.21%. Spot on the other hand moved 3% over the same period.

Over longer time horizons, traders can still make significant profits. Looking at 2 days

![Image of Twap Lag With Spread And Vol Zoom Out Plot](../assets/oip-1/twap_lag_double_spread_vol_zoom_1x.png)

and 3 months of simulated data

![Image of Twap Lag With Spread Full Plot](../assets/oip-1/twap_lag_double_spread_all.png)

shows markets remain tradeable.


## Spot Manipulation

Uniswap offers the TWAP as a method for offering a [manipulation-resistant on-chain oracle](https://uniswap.org/whitepaper.pdf).

<!--

However, we're suggesting using *both* the TWAP and the current spot price to determine what entry and exit prices to give traders. At first glance, [this is rather concerning](https://samczsun.com/taking-undercollateralized-loans-for-fun-and-for-profit/).

Are Overlay markets now susceptible to manipulation of the spot price?

Take the example of an attacker manipulating the spot price upward. In another round of sims, we add a shock of ~10% over 100 blocks

![Image of Twap Attack Plot](../assets/oip-1/twap_attack.png)

to use as an example.

**Q: Are we comparing the rate against known good rates as samczsun suggests? There's an attack potentially with spot manipulation**

![Image of Twap Attack With Spread Plot](../assets/oip-1/twap_attack_spread.png)

*NOTE: There is a possible attack on others positions: user manipulates the spot price to cause other user's queued OI to settle at a worse price than they would have had otherwise. This grief attack doesn't cause any profit for the user who is causing it however so it's a complete burning of capital. Given liquid spot markets take significant amounts of capital to manipulate, it seems unlikely we should be overly concerned about this griefing attack.*
*
* -->


## Calibrating \\( S \\)

\\( S \\), as an additional static spread, offers protection against large jumps in spot that happen over shorter timeframes than \\( \nu \\). To calibrate, we can use the statistical properties of the underlying feed.

Our goal is to have the static spread \\( e^{\pm S} \\) produce bid and ask values that e.x. 97% of the time will be worse than any jumps that are likely to occur in the spot price over a 10 minute interval. This guards against the timelag associated with the shorter 10 minute TWAP versus the actual spot price.

To accomplish this, we suggest setting the spread to

\\[ S = \frac{\mu \cdot (\nu - 1)}{2} + C(a, \nu) \cdot \sigma F^{-1}_{ab}(1-\alpha) \\]

where

\\[ C(a, \nu) \equiv \bigg[ \frac{\nu}{a} \bigg(1 - \bigg(\frac{1}{\nu}\bigg)^{a} \cdot \frac{\nu+1}{2} \bigg) \bigg]^{\frac{1}{a}} \\]

\\( F^{-1}_{ab} \\) is the inverse CDF for the standard [Levy stable](https://en.wikipedia.org/wiki/Stable_distribution) \\( S(a, b, 0, 1) \\).

\\( 1-\alpha \\) is the probability that our offered ask (bid) price is worse for the trader than the future spot price, given a move up (down).

\\( \mu \\), \\( \sigma \\), \\( a \\) and \\( b \\) are parameters expressed per-block above, fit using historical data assuming log-stable increments for the underlying spot price

\\[ P(t+\tau) = P(t) e^{\mu \tau + \sigma L\_{\tau}} \\]

where \\( L\_{\tau} \sim S(a, b, 0, (\frac{\tau}{a})^{1/a}) \\).


### Concrete Numbers

We use [`pystable`](https://github.com/overlay-market/pystable) to fit the last 120 days of 10 minute data from the [USDC-WETH SushiSwap pool](https://analytics.sushi.com/pairs/0x397ff1542f962076d0bfe58ea045ffa2d347aca0).


### Derivation

Formally, we want the probability that the spot price \\( P \\) is greater than the ask price, \\( \nu \\) blocks into the future, to be equal to a small number \\( \alpha \\):

$$\begin{eqnarray}
\alpha &=& \mathbb{P}[ P(t+\nu) > A(t+\nu) | P(t+\nu) > P(t) ] \\
&=& \mathbb{P}[ P(t+\nu) > \mathrm{TWAP}(t, t+\nu) \cdot e^{S} ]
\end{eqnarray}$$

In the case of a spot jump up, we look at spot prices greater than the ask. For a spot jump down, we would look at spot prices less than the bid. Assume the current time is \\( t \\).

Take spot to be driven by a [Levy process](https://en.wikipedia.org/wiki/L%C3%A9vy_process)

\\[ P(t+\tau) = P(t) e^{\mu \tau + \sigma L_{\tau}} \\]

with log-stable increments. The future value of the geometric TWAP averaged over \\( \nu \\) blocks will be

$$\begin{eqnarray}
\mathrm{TWAP}(t, t+\nu) &=& \bigg( \prod_{t' = t}^{t+\nu} P(t') \bigg)^{\frac{1}{\nu}} \\
&=& P(t) e^{\frac{1}{\nu} \sum_{t''=0}^{\nu} \mu t'' + \sigma L_{t''}} \\
&=& P(t) e^{\frac{\mu (\nu + 1)}{2} + \frac{\sigma}{\nu} L_{\frac{\nu (\nu + 1)}{2}}}
\end{eqnarray}$$

using some arithmetic series math and [properties of sums of stable random variables](https://en.wikipedia.org/wiki/Stable_distribution#Properties).


## Market Impact
