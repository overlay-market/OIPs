---
note: 12
oip-num: 1
title: Single-Sided Liquidity Mining
status: WIP
author: Michael Feldman (@mikeyrf)
discussions-to: oip-1
created: 2021-04-12
updated: N/A
---

This note aims to address the following issues:

- Can we replicate single-sided liquidity mining by creating vaults that simultaneously stake in pool 2 (Uni V3 ETH/OVL LPs) while taking out long or short positions on the corresponding Overlay market?


## Summary

The benefit of having an Overlay market on ETH/OVL while liquidity miners stake their Uni V3 ETH/OVL LP tokens is those same liquidity miners can construct a portfolio on-chain that uses the Overlay market to hedge out some of the underlying spot LP exposure to the token they least prefer.

For miners that prefer exposure only to OVL, users can

- Liquidity mine with ETH/OVL LP tokens to earn OVL rewards
- Take out a 1x short on ETH/OVL to hedge LP spot exposure to ETH

The strategy will replicate (to a degree) staking OVL alone to earn OVL rewards.

For miners that prefer exposure only to ETH, users can

- Borrow OVL with ETH
- Liquidity mine with ETH/OVL LP tokens to earn OVL rewards
- Take out a 1x long on ETH/OVL to hedge LP spot exposure to OVL

The strategy will replicate (to a degree) staking ETH alone to earn OVL rewards.

The downside to both strategies is the user still experiences impermanent loss (can't be hedged out with Overlay positions) and now has to worry about the funding rate on the Overlay market. The upside is replication of single-sided staking when ignoring impermanent loss and funding.

From a protocol perspective, the upside to these strategies is there should exist natural demand to position on Overlay markets from liquidity miners.


## Replicating Portfolio

Assume:

- Liquidity miners are incentivized to stake ETH/OVL LP tokens to earn OVL rewards
- An Overlay market on ETH/OVL has been launched
- A lending pool with OVL and ETH deposits exists on a lending protocol

Ignore funding from holding the Overlay position.

Ignore impermanent loss from holding the LP tokens by assuming the amount of spot ETH and OVL held throughout remains 50/50.

Take the price \\( P(t) \\) of the Uni V3 ETH/OVL TWAP feed to be in units of number of OVL / number of ETH (i.e. ETH is the base, OVL is the quote). The value of the LP token without impermanent loss in OVL terms is simply

\\[ V_{LP}(t) = N + \frac{N}{P(0)} \cdot P(t) \\]

at some time \\( t \geq 0 \\) in the future, for \\( N \\) OVL and \\( \frac{N}{P(0)} \\) ETH initially deposited to the spot pool for the LP token.

### Single-Sided OVL Staking

To replicate liquidity mining by only staking OVL, the user that prefers exposure to only OVL can take out a 1x short on the Overlay market for ETH/OVL in addition to their LP token exposure.

The value of the 1x short in OVL terms will be approximately

\\[ V_{short}(t) = N - \frac{N}{P(0)} \cdot \bigg[ P(t) - P(0) \bigg] \\]

when ignoring funding, for an initial \\( N \\) OVL of collateral deposited to back the position.

Total value of the vault with OVL preference in OVL terms is then

$$\begin{eqnarray}
V_{vault} (t) &=& V_{LP}(t) + V_{short}(t) \\
&=& 3 N
\end{eqnarray}$$

which is independent of the price of ETH relative to OVL. The replicating portfolio acts like \\( 3N \\) worth of OVL collateral, when ignoring funding and impermanent loss.

### Single-Sided ETH Staking

To replicate liquidity mining by only staking ETH, the user that prefers exposure to only ETH can borrow OVL with ETH collateral and take out a 1x long on the Overlay market for ETH/OVL in addition to their LP token exposure.

The value of the 1x long in OVL terms will be approximately

\\[ V_{long} (t) = N + \frac{N}{P(0)} \cdot \bigg[ P(t) - P(0) \bigg] \\]

when ignoring funding, for an initial \\( N \\) OVL of collateral deposited to back the position. To obtain that initial amount of OVL collateral, the user takes out an ETH collateralized loan of \\( N \\) OVL from a lending protocol, for a vault debt in OVL terms of

\\[ V_{debt}(t) = -N \\]

Total value of the vault with ETH preference in OVL terms is then

$$\begin{eqnarray}
V_{vault} (t) &=& V_{LP}(t) + V_{long}(t) + V_{debt}(t) \\
&=& 2 \cdot \frac{N}{P(0)} \cdot P(t)
\end{eqnarray}$$

which in ETH terms

$$\begin{eqnarray}
V^{ETH}_{vault} (t) &=& \frac{V_{vault}(t)}{P(t)} \\
&=& 2 \cdot \frac{N}{P(0)}
\end{eqnarray}$$

is independent of the price of ETH relative to OVL. The replicating portfolio acts like \\( 2 \cdot \frac{N}{P(0)} \\) worth of ETH collateral, when ignoring funding and impermanent loss.


## Impermanent Loss & Funding


## Countering with Basis Trading
