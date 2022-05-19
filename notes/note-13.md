---
note: 13
oip-num: 1
title: No-Arbitrage Imbalance
status: WIP
author: Michael Feldman (@mikeyrf)
discussions-to: oip-1
created: 2022-05-19
updated: N/A
---

This note aims to address the following issues:

- What is the open interest imbalance in the no-arbitrage limit?
- What is the exposure the protocol assumes in the no-arbitrage limit?


## Summary

From Equations (29)-(31) of the [V1 Core whitepaper](https://planckcat.mypinata.cloud/ipfs/QmVMX7DH8Kh22kxMyDFGUJcw1a3irNPvyZBtAogkyJYJEv), funding is given by

\\[ f = 2k \cdot I \\]

where

\\[ I \equiv \frac{\mathrm{OI}\_{imb}}{\mathrm{OI}\_{tot}} \\]

\\( f > 0 \\) implies longs pay shorts and the opposite for \\( f < 0 \\).

[Covered interest rate parity](https://en.wikipedia.org/wiki/Interest_rate_parity#Covered_interest_rate_parity) implies the expected funding rate paid by the longs to the shorts in the no-arbitrage limit will be

\\[ f_Q = r_{quote} - r_{base} = r_Q \\]

the difference in "risk-free" rates between the quote and base currencies of the inverse market. In practice, the "risk-free" rate for OVL should be the yield on the single-sided staking liquidity mining pool (Overlay's version of T-notes). Similarly for ETH, the "risk-free" rate should be the yield from ETH 2 staking. See [this series](https://nopeitslily.substack.com/p/risk-frees-and-currencies-part-three?utm_source=%2Fprofile%2F26558147-lily-francus&utm_medium=reader2&s=r) by Lily Francus for the argument.

The risk-neutral open interest imbalance would then be

\\[ I\_{Q} = \frac{r_{Q}}{2k} \\]


## PnL Liability

From Equation (32) of the V1 Core WP, the protocol is liable for

\\[ \mathrm{PnL}\_{liability}(\tau) = -\mathrm{OI}\_{b_r}(\tau) \cdot P(0) + \mathrm{OI}\_{imb}(\tau) \cdot [P(\tau) - P(0)] \\]

at a time \\( t=\tau \\) in the future. \\( t = 0 \\) is now. \\( \mathrm{OI}\_{imb} \\) is the open interest imbalance over time. \\( \mathrm{OI}\_{b_r} \\) is the open interest "burned" / removed from the system given the protocol's exposure to the market due to the imbalance.

The profit liability is the amount of OVL the protocol has to print given the initial open interest imbalance at the current time.

Note that

$$\begin{eqnarray}
\mathrm{OI}_{imb}(\tau) &=& \mathrm{OI}_{imb}(0) \cdot e^{-2k\tau} \\
\mathrm{OI}_{b_r}(\tau) &=& \mathrm{OI}_{tot}(0) \cdot \bigg[ 1 - \sqrt{1 - \bigg(\frac{\mathrm{OI}_{imb}(0)}{\mathrm{OI}_{tot}(0)}\bigg)^2 \cdot \bigg( 1 - e^{-4k\tau} \bigg)} \bigg]
\end{eqnarray}$$

To simplify the math for the purposes of this note, take the spot price to be driven by a Wiener process

\\[ \frac{P(t)}{P(0)} = e^{(r - \frac{\sigma^2}{2}) \tau + \sigma W_{\tau}} \\]

with drift \\( r \\) and volatility \\( \sigma \\). Then, the expected value is given by

\\[ \mathbb{E}^Q\bigg[ \frac{P(t)}{P(0)} \bigg] = e^{r_Q\tau} \\]

under the risk-neutral measure \\( Q \\).

### General

Graph of PnL liability *not* necessarily assuming no-arbitrage imbalance level at \\( t=0 \\).

<iframe src="https://www.desmos.com/calculator/co2ymz2lfm?embed" width="500" height="500" style="border: 1px solid #ccc" frameborder=0></iframe>


### No-Arbitrage

Graph of PnL liability assuming no-arbitrage imbalance level at \\( t=0 \\).

<iframe src="https://www.desmos.com/calculator/ovc5q9j0c2?embed" width="500" height="500" style="border: 1px solid #ccc" frameborder=0></iframe>


## Stability

The system appears very stable when \\( r \ll 2k \\), particularly assuming the no-arbitrage limit. Stable in the sense of inflation of currency supply is nominal given profit liability charts.

The system appears to potentially become unstable when \\( r \geq 2k \\) and no-arbitrage breaks down. Additional circuit breaker and cap mechanisms limit the damage to this type of tail event.

To verify stability, one can look at the first and second derivative of the expected value under the risk-neutral measure of the profit liability with respect to time in the limit as \\( t \to 0 \\)

$$\begin{eqnarray}
\lim_{\tau \to 0} \frac{d}{d\tau} \mathbb{E}^Q\bigg[\mathrm{PnL}_{liability}(\tau)\bigg] &=& P(0) \cdot \mathrm{OI}_{imb}(0) \cdot \bigg( r_Q - f_Q \bigg) = 0 \\
\lim_{\tau \to 0} \frac{d^2}{d\tau^2} \mathbb{E}^Q\bigg[\mathrm{PnL}_{liability}(\tau)\bigg] &=& P(0) \cdot \mathrm{OI}_{imb}(0) \cdot r_Q \cdot \bigg( r_Q - 2k \bigg)
\end{eqnarray}$$

This imposes a condition on our governance chosen value for \\( k \\) in order to achieve a concave liability function in time

\\[ \lim_{\tau \to 0} \frac{d^2}{d\tau^2} \mathbb{E}^Q\bigg[\mathrm{PnL}_{liability}(\tau)\bigg] < 0 \\]

Fortunately, we calibrate \\( k \\) using VaR at 95, 99% levels, which will produce \\( r_Q \ll 2k \\). As long as this condition holds, the system should be stable.

Governance will need to monitor \\( r_Q \\) vs \\( 2k \\) continuously and adjust \\( k \\) accordingly in the event the spread in "risk-free" rates between OVL and e.g. ETH increases significantly.
