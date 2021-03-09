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

- How is \\( k \\) related to the risk a market feed imposes on the system?


## The Setup

Return to the functional form of our [funding payments](note-1) \\( \mathrm{FP}_i \\)

\\[ \mathrm{FP}\_i = k \cdot \mathrm{TWAOI}\_{imb}(t_i) \\]

where \\( \mathrm{TWAOI}\_{imb} = \mathrm{TWAOI}_l - \mathrm{TWAOI}_s \\) is the time-weighted average of the open interest imbalance between the long and short side on a market.

We need some guidance on what to set the value of \\( k \\) as for every update period. \\( k \\) dictates the rate at which funds flow from longs to shorts or shorts to longs to rebalance the system and draw down the risk associated with an imbalanced book. Thus, \\( k \\) should be related to the risk the underlying feed imposes on the system and inherently passive OVL holders through the currency supply.

To start, consider the case where \\( \mathrm{OI}_{imb} > 0 \\) so longs outweigh shorts. For simplicity within this section, assume time-weighted averages are equivalent to their associated open interest values such that \\( \mathrm{TWAOI} = \mathrm{OI} \\). Further, assume no more positions are taken or exited on either side such that the total open interest remains a constant: \\( \mathrm{OI}_l + \mathrm{OI}_s = \mathrm{const} \\). The latter assumption will skew our risk estimates, but likely to the more conservative side given funding incentives should trend towards a more balanced book over time.

What does the evolution of the imbalance look like over time  when we factor in funding payments? Given an open interest on a market \\( X \\) for the long side of \\( \mathrm{OI}_l \\) and short side of \\( \mathrm{OI}_s \\), take the imbalance on the market at time \\( t_i \\) to be \\( {\mathrm{OI}\_{imb}}\_i = {\mathrm{OI}_l}_i - {\mathrm{OI}_s}_i > 0 \\). In terms of the prior period \\( t\_{i-1} \\), open interest on the long side after paying the funding payment will be

\\[ {\mathrm{OI}\_{l}}_i = {\mathrm{OI}\_{l}}\_{i-1} - \mathrm{FP}\_{i-1} \\]

and short side after receiving funding

\\[ {\mathrm{OI}\_{s}}_i = {\mathrm{OI}\_{s}}\_{i-1} + \mathrm{FP}\_{i-1} \\]

Subtracting these two and expanding \\( \mathrm{FP}_{i-1} \\) gives the time evolution of the imbalance from block \\( i-1 \\) to block \\( i \\)

\\[ {\mathrm{OI}\_{imb}}_i = {\mathrm{OI}\_{imb}}\_{i-1} \cdot ( 1 - 2k ) \\]

Rinse and repeat \\( i \\) times to get the time evolution as a function of the value of the open interest imbalance when traders initially enter their positions

\\[ {\mathrm{OI}\_{imb}}_i = {\mathrm{OI}\_{imb}}\_{0} \cdot ( 1 - 2k )^i \\]

where \\( k \in [0, 0.5] \\).

One can view the risk to the system at time \\( t_0 \\) due to the long imbalance created on this market as the expected PnL the system would need to pay out to a long position with notional \\( \mathrm{OI}_{imb} \\) at some time in the future \\( t_i \\):

\\[ {\mathrm{PnL}\_{imb}}_i = {\mathrm{OI}\_{imb}}\_{i} \cdot \bigg[ \frac{P_i}{P_0} - 1 \bigg] \\]

where \\( P_i = P(t_i) \\) is the future value of the underlying feed at time \\( t_i \\) and \\( P_0 \\) the value at the current time \\( t_0 \\). Take \\( P : \Omega \xrightarrow{} \mathbb{R} \\) to be a random variable on the probability space \\( (\Omega, \mathcal{F}, \mathrm{P}) \\) driven by a stochastic process \\( W_t \\)

\\[ P_t = P_0 e^{\mu \cdot t + \sigma \cdot W_t} \\]

such that the feed exhibits Geometric Brownian motion (GBM) when \\( W_t \\) is a Wiener process. Assume GBM for now even though DeFi price feeds will be far more fat-tailed (we'll have to be more conservative with \\( k \\) values chosen). PnL at time \\( t_i \\) from this hypothetical long position reduces to

\\[ {\mathrm{PnL}\_{imb}}_i = {\mathrm{OI}\_{imb}}\_{0} \cdot ( 1 - 2k )^i \cdot \bigg[ e^{\mu \cdot i \cdot T + \sigma \cdot W\_{i \cdot T}}  - 1 \bigg] \\]

where \\( t_i - t_0 = i \cdot T \\) and \\( T \\) is the length of time between funding payments.

Our approach will be to choose a \\( k \\) that minimizes the expected value of the PnL, \\( \mathbb{E}[ {\mathrm{PnL}\_{imb}}\_i \| \mathcal{F}_{i} ] \\), for this "position" within a finite number \\( i \\) time intervals to reduce risk to the system. Taking the expected value of above

\\[ \mathbb{E}[ {\mathrm{PnL}\_{imb}}\_i \| \mathcal{F}_{i} ] = {\mathrm{OI}\_{imb}}\_{0} \cdot ( 1 - 2k )^i \cdot \bigg[ e^{\mu \cdot i \cdot T} \cdot \mathbb{E}[e^{\sigma \cdot W\_{i \cdot T}}]  - 1 \bigg] \\]

But, using \\( W_{i \cdot T} \sim \mathcal{N}(0, i \cdot T) \\) and the PDF of the [normal distribution](https://en.wikipedia.org/wiki/Normal_distribution), \\( \mathbb{E}[e^{\sigma \cdot W\_{i \cdot T}}] = (1 / \sqrt{2 \pi}) \int_{\mathbb{R}} dz \; e^{\sigma \cdot \sqrt{i \cdot T} \cdot z - z^2 / 2} = e^{\sigma^2 \cdot i \cdot T / 2} \cdot (1 / \sqrt{2 \pi}) \int_{\mathbb{R}} dz' \; e^{- z'^2 / 2} = e^{\sigma^2 \cdot i \cdot T / 2} \\), reducing our expression for the expected value the system needs to pay out for the imbalance to

\\[ \mathbb{E}[ {\mathrm{PnL}\_{imb}}\_i \| \mathcal{F}_{i} ] = {\mathrm{OI}\_{imb}}\_{0} \cdot ( 1 - 2k )^i \cdot \bigg[ \bigg(e^{(\mu + \sigma^2 / 2) \cdot T} \bigg)^i  - 1 \bigg] \\]

Let \\( a = 1 / (1 - 2k) \\), where \\( a \in [1, \infty] \\):

\\[ \mathbb{E}[ {\mathrm{PnL}\_{imb}}\_i \| \mathcal{F}_{i} ] = {\mathrm{OI}\_{imb}}\_{0} \cdot a^{-i} \cdot \bigg[ \bigg(e^{(\mu + \sigma^2 / 2) \cdot T} \bigg)^i  - 1 \bigg] \\]

Our task then becomes choosing a value for \\( a \gg e^{(\mu + \sigma^2 / 2) \cdot T} \\) such that the expected value of the imbalance profit significantly decays over time as more blocks go by. Notice, this relates our chosen value for \\( k \\) to properties of the underlying feed (i.e. drift and volatility).
