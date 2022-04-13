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

- Can we replicate single-sided liquidity mining by creating vaults that simulatenously stake in pool 2 (Uni V3 ETH/OVL LPs) while taking out long or short positions on the corresponding Overlay inverse market?


## Summary

The benefit of having an Overlay market on ETH/OVL while liquidity miners stake their Uni V3 ETH/OVL LP tokens is those same liquidity miners can construct a portfolio on-chain that uses the Overlay market to hedge out some of the underlying spot LP exposure to the token they least prefer.

For miners that prefer exposure only to OVL, traders can

- Liquidity mine with ETH/OVL LP tokens to earn OVL rewards
- Take out a 1x short on ETH/OVL to hedge LP spot exposure to ETH
- Earn rewards in OVL

For miners that prefer exposure only to ETH, traders can

- Borrow OVL with ETH
- Liquidity mine with ETH/OVL LP tokens to earn OVL rewards
- Take out a 1x long on ETH/OVL to hedge LP spot exposure to OVL
- Earn rewards in OVL


The latter strategy for traders who prefer to denominate in ETH requires a pool on a lending protocol to exist. The former strategy for traders who prefer OVL has no such requirement.


## Replicating Portfolio

### OVL Denominators


### ETH Denominators


## Impermanent Loss & Funding
