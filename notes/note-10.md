---
note: 10
oip-num: 1
title: Cost of Attack - Balancer V2
status: WIP
author: Michael Feldman (@mikeyrf)
discussions-to: oip-1
created: 2021-11-24
updated: N/A
---

Two issues to address with this note:

- What is the cost to attack an Overlay market that uses Balancer V2 price oracles, if the attacker manipulates the spot pool?

- How do we prevent this type of spot manipulation attack?


## Context

Balancer V2 is the only existing AMM that offers *both* historical snapshots of price and liquidity accumulator values queryable on-chain and a deterministic liquidity profile. The combination of these two makes it possible for us to offer a reliable market on their geometric TWAP oracles, as we can use their liquidity oracle to adjust our open interest caps such that the spot manipulation trade is never profitable.

The backrunning attack works like so:

1. Alice takes out an Overlay position on the Balancer V2 spot TWAP feed
2. Alice swaps tokens through the spot pool for \\( \nu \\) blocks to increase/decrease price in her Overlay position's favor
3. Alice exits the Overlay position

My prior note examining [cost of attack for Uniswap V2 TWAPs](note-2) incorrectly assumed that all capital used to swap on spot for the manipulation would be lost. In reality, the attacker only loses to slippage as they receive tokens out from the spot pool. The difference in capital required to execute the attack becomes apparent when the attacker manipulates the pool over multiple blocks within the averaging window (little is lost to slippage) vs over just one block (most is lost to slippage).

I'll use this note for a more proper derivation of cost of attack and an implementable (via our market contracts) mitigation strategy to make this attack unprofitable in all reasonable instances.

## Balancer Math
