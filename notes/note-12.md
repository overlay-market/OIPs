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

For miners that prefer exposure only to OVL, traders can

- Liquidity mine with ETH/OVL LP tokens to earn OVL rewards
- Take out a 1x short on ETH/OVL to hedge LP spot exposure to ETH

The strategy will replicate (to a degree) staking OVL alone to earn OVL rewards.

For miners that prefer exposure only to ETH, traders can

- Borrow OVL with ETH
- Liquidity mine with ETH/OVL LP tokens to earn OVL rewards
- Take out a 1x long on ETH/OVL to hedge LP spot exposure to OVL

The strategy will replicate (to a degree) staking ETH alone to earn OVL rewards.

The downside to both strategies is the trader still experiences impermanent loss (can't be hedged out with Overlay positions) and now has to worry about the funding rate on the Overlay market. The upside is replication of single-sided staking when ignoring impermanent loss and funding.

From a protocol perspective, the upside to these strategies is there should exist natural demand to trade on Overlay markets from liquidity miners.


## Replicating Portfolio

### OVL Denominators


### ETH Denominators


## Impermanent Loss & Funding
