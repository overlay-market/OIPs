---
note: 4
oip-num: 1
title: Risk and the Funding Constant
status: WIP
author: Michael Feldman (@mikeyrf)
discussions-to: oip-1
created: 2021-03-08
updated: N/A
---

Two issues to address with this note:

- What should we set the constant \\( k \\) to be in each of our funding payments?

- How is \\( k \\) related to the risk a market feed adds to the system?


## Context

Return to the functional form of our [funding payments](note-1) \\( \mathrm{FP}_n \\)

\\[ \mathrm{FP}\_n = k \cdot \mathrm{TWAOI}\_{imb}(t_n) \\]

where \\( {\mathrm{TWAOI}\_{imb}}_n = {\mathrm{TWAOI}_l}_n - {\mathrm{TWAOI}_s}_n \\) is the time-weighted average of the open interest imbalance between the long and short side on a market at time \\( t_n \\).

We need some guidance on what to set the value of \\( k \\) as for every update period. \\( k \\) dictates the rate at which funds flow from longs to shorts or shorts to longs to rebalance the system and draw down the risk associated with an imbalanced book. Thus, \\( k \\) should be related to the risk the underlying feed adds to the system and inherently passive OVL holders through the currency supply.

To start, consider the case where \\( \mathrm{OI}_{imb} > 0 \\) so longs outweigh shorts. For simplicity, assume time-weighted averages are equivalent to their associated open interest values such that \\( \mathrm{TWAOI} = \mathrm{OI} \\). Further, assume no more positions are built or unwound on either side such that the total open interest remains a constant: \\( \mathrm{OI}_l + \mathrm{OI}_s = \mathrm{const} \\). The latter assumption will skew our risk estimates, but likely to the more conservative side given funding incentives should trend towards a more balanced book over time.


## Risk-Based Approach to Balancing Markets

### Imbalance Over Time

What does the evolution of the imbalance look like over time  when we factor in funding payments? Given open interest on a market for the long side of \\( \mathrm{OI}_l \\) and short side of \\( \mathrm{OI}_s \\), take the imbalance on the market at time \\( t_n \\) to be \\( {\mathrm{OI}\_{imb}}\_n = {\mathrm{OI}_l}_n - {\mathrm{OI}_s}_n > 0 \\). In terms of the prior period \\( t\_{n-1} \\), open interest on the long side after paying the funding payment will be

\\[ {\mathrm{OI}\_{l}}_n = {\mathrm{OI}\_{l}}\_{n-1} - \mathrm{FP}\_{n-1} \\]

and short side after receiving funding

\\[ {\mathrm{OI}\_{s}}_n = {\mathrm{OI}\_{s}}\_{n-1} + \mathrm{FP}\_{n-1} \\]

Subtracting the two and expanding \\( \mathrm{FP}_{n-1} \\) gives the time evolution of the imbalance from block \\( n-1 \\) to block \\( n \\)

\\[ {\mathrm{OI}\_{imb}}_n = {\mathrm{OI}\_{imb}}\_{n-1} \cdot ( 1 - 2k ) \\]

Rinse and repeat \\( n \\) times to get the time evolution as a function of the value of the open interest imbalance when traders initially enter their positions

\\[ {\mathrm{OI}\_{imb}}_n = {\mathrm{OI}\_{imb}}\_{0} \cdot ( 1 - 2k )^n \\]

where \\( k \in [0, \frac{1}{2}] \\).


### Risk to the System

One can view the risk to the system at time \\( t_0 \\) due to the long imbalance created on this market as the expected PnL the system would need to pay out to a long position with notional \\( {\mathrm{OI}_{imb}}_0 > 0 \\) at some time in the future \\( t_n \\):

\\[ {\mathrm{PnL}\_{imb}}_n = {\mathrm{OI}\_{imb}}\_{n} \cdot \bigg[ \frac{P_n}{P_0} - 1 \bigg] \\]

where \\( P_n = P(t_n) \\) is the future value of the underlying feed at time \\( t_n \\) and \\( P_0 \\) the value at the current time \\( t_0 \\). Take \\( P : \Omega \to \mathbb{R} \\) to be a random variable on the probability space \\( (\Omega, \mathcal{F}, \mathrm{P}) \\) driven by a stochastic process \\( W_t \\)

\\[ P_t = P_0 e^{\mu \cdot t + \sigma \cdot W_t} \\]

such that the feed exhibits Geometric Brownian motion (GBM) when \\( W_t \\) is a Wiener process. Assume GBM for now even though DeFi price feeds will be far more fat-tailed, particularly for feeds with stablecoins as the quote currency (we'll have to be more conservative with \\( k \\) values chosen). PnL at time \\( t_n \\) from this hypothetical long position reduces to

\\[ {\mathrm{PnL}\_{imb}}_n = {\mathrm{OI}\_{imb}}\_{0} \cdot ( 1 - 2k )^n \cdot \bigg[ e^{\mu \cdot n \cdot T + \sigma \cdot W\_{n \cdot T}}  - 1 \bigg] \\]

where \\( t_n - t_0 = n \cdot T \\) and \\( T \\) is the length of time between funding payments.

Our approach will be to choose a \\( k \\) that minimizes the expected value of the PnL, \\( \mathbb{E}[ {\mathrm{PnL}\_{imb}}\_n \| \mathcal{F}_{n} ] \\), for this "position" within a finite number \\( n \\) time intervals to reduce risk to the system. Taking the expected value of above

\\[ \mathbb{E}[ {\mathrm{PnL}\_{imb}}\_n \| \mathcal{F}_{n} ] = {\mathrm{OI}\_{imb}}\_{0} \cdot ( 1 - 2k )^n \cdot \bigg[ e^{\mu \cdot n \cdot T} \cdot \mathbb{E}[e^{\sigma \cdot W\_{n \cdot T}}]  - 1 \bigg] \\]

But, using \\( W_{n \cdot T} \sim \mathcal{N}(0, n \cdot T) \\) and the PDF of the [normal distribution](https://en.wikipedia.org/wiki/Normal_distribution), \\( \mathbb{E}[e^{\sigma \cdot W\_{n \cdot T}}] = (1 / \sqrt{2 \pi}) \int_{\mathbb{R}} dz \; e^{\sigma \cdot \sqrt{n \cdot T} \cdot z - z^2 / 2} = e^{\sigma^2 \cdot n \cdot T / 2} \cdot (1 / \sqrt{2 \pi}) \int_{\mathbb{R}} dz' \; e^{- z'^2 / 2} = e^{\sigma^2 \cdot n \cdot T / 2} \\), simplifying our expression for the expected value the system needs to pay out for the imbalance to

\\[ \mathbb{E}[ {\mathrm{PnL}\_{imb}}\_n \| \mathcal{F}_{n} ] = {\mathrm{OI}\_{imb}}\_{0} \cdot ( 1 - 2k )^n \cdot \bigg[ \bigg(e^{(\mu + \sigma^2 / 2) \cdot T} \bigg)^n  - 1 \bigg] \\]

Let \\( a = \frac{1}{1 - 2k} \\), where \\( a \in [1, \infty) \\):

\\[ \mathbb{E}[ {\mathrm{PnL}\_{imb}}\_n \| \mathcal{F}_{n} ] = {\mathrm{OI}\_{imb}}\_{0} \cdot a^{-n} \cdot \bigg[ \bigg(e^{(\mu + \sigma^2 / 2) \cdot T} \bigg)^n  - 1 \bigg] \\]

This reduces our task to choosing an appropriate value for \\( a \gg e^{(\mu + \sigma^2 / 2) \cdot T} \\) such that the expected value of the imbalance profit significantly decays over time as more blocks go. Take

\\[ a = b \cdot e^{(\mu + \sigma^2 / 2) \cdot T} \\]

where \\( b \in (1, \infty) \\). As \\( n \to \infty \\),

\\[ \lim_{n\to\infty} \mathbb{E}[ {\mathrm{PnL}\_{imb}}\_n \| \mathcal{F}_{n} ] = {\mathrm{OI}\_{imb}}\_{0} \cdot \bigg( \frac{e^{(\mu + \sigma^2 / 2) \cdot T}}{a} \bigg)^n = \frac{ {\mathrm{OI}\_{imb}}\_0 }{b^n} = 0 \\]

In terms of \\( k \\)

\\[ k = \frac{1}{2} \cdot \bigg[ 1 - \frac{1}{b \cdot e^{(\mu + \sigma^2 / 2) \cdot T}} \bigg] \\]

Notice, this relates our chosen value for \\( k \\) to properties of the underlying feed (i.e. drift and volatility).


### Value at Risk

Expanding further, we can examine the value at risk (VaR) to the system for paying out PnL on this hypothetical long position due to our market's imbalance. Note, the protocol and passive OVL holders are taking the other side, so what we really want is the probability \\( 1 - \alpha \\) this imbalance PnL is less than an amount \\( \mathrm{VaR}_{\alpha, n} \\):

\\[ 1 - \alpha = \mathbb{P}[ {\mathrm{PnL}\_{imb}}\_n \leq \mathrm{VaR}_{\alpha, n} ] \\]

where we abuse notation here given the [usual definition of VaR](https://en.wikipedia.org/wiki/Value_at_risk). From the prior section,

\\[ 1 - \alpha = \mathbb{P}\bigg[{\mathrm{OI}\_{imb}}\_{0} \cdot a^{-n} \cdot \bigg( e^{\mu \cdot n \cdot T + \sigma \cdot W\_{n \cdot T}}  - 1 \bigg) \leq \mathrm{VaR}_{\alpha, n} \bigg] \\]

which reduces to

\\[ 1 - \alpha = \Phi \bigg( \frac{1}{\sigma \cdot \sqrt{n \cdot T}} \cdot \bigg[ \ln \bigg( 1 + a^{n} \cdot \tilde{\mathrm{VaR}}_{\alpha, n} \bigg) - \mu \cdot n \cdot T \bigg] \bigg) \\]

\\( \tilde{\mathrm{VaR}}_{\alpha, n} = \frac{\mathrm{VaR}\_{\alpha, n}}{ {\mathrm{OI}\_{imb}}\_{0} } \\) is normalized for the original imbalance amount and \\( \Phi (z) = \mathbb{P}[ Z \leq z ] \\) is the CDF of the standard normal distribution \\( Z \sim \mathcal{N}(0, 1) \\). Inverting this, one finds the normalized upper bound for the PnL to be paid out, \\( \tilde{\mathrm{VaR}}\_{\alpha, n} \\), as a function of the (\\( 1 - \alpha \\))-quantile:

\\[ \tilde{\mathrm{VaR}}_{\alpha, n} = a^{-n} \cdot \bigg[ \bigg( e^{\mu \cdot T + \sigma \cdot \sqrt{T/n} \cdot {\Phi}^{-1}(1-\alpha)} \bigg)^n - 1 \bigg] \\]

Anticipated VaR to the system also scales with \\( a^{-n} \\), supporting a choice of \\( a \gg e^{(\mu + \sigma^2 / 2) \cdot T} \\).


### Choice of \\( k \\)

<!-- TODO: Determining \\( \mu \\) and \\( \sigma^2 \\) -->
