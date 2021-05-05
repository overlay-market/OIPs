note: X
oip-num: 1
title: Pooling Stability Funds
status: WIP
author: Adam Kay (@mcillkay)
discussions-to: oip-1
created: 2021-04-17
updated: N/A
---

Issue to address with this note:

- How do we realize the potential for huge capital pools to stabilize the system by making yield on funding?


## Context

[A previous note](note-1) explored the ability of a funding payment mechanism to incentivize yield hunters to balance the Overlay system directional risk. These actors seek yield on either OVL or ETH (or possibly a stablecoin), without taking directional risk. In this note they will be called *investors*. In practice there are some difficulties with the approach:


1. To remain profitable, investors must remain nimble, reacting quickly to changes in the imbalance. Failure to do so will reduce yield or even incur loss. Thus investors must be fairly high frequency.

2. As the system scales, investors who wish to gain yield must keep track of an increasing number of markets.

3. Moreover, small imbalances on multiple markets might not be worth balancing for investors individually, but collectively might represent a significant risk to the system.   

4. The stragegy that has investors gaining yield on OVL on the OVL-ETH feed requires them to first sell half their OVL for spot ETH. This becomes increasingly difficult as Overlay scales to many assets across multiple exchanges, and  it is impossible for non-financial markets such as pure scalar data feeds (e.g. the CPI).

These issues collectively assure that the balancing mechanism will be a specialized activity, requiring ongoing maintenance and incurring technical debt. This complexity acts as a limit to investor participation, which then becomes a bottleneck for the system itself.  


## Passive Balancing Pools

### Summary

To allow for an Overlay-managed pool, similar to a Yearn vault, which incurs zero transactions fees, takes the opposite side of the imbalance on *all* Overlay markets collectively, and allows for yield on both OVL and ETH.

### Noop


### Basic Idea

On ETH-OVL market, someone opens a long position of $$n$$ OVL (effectively selling OVL and buying ETH). In order to balance this position, the pool would need to short the same feed with size $$\alpha n$$ for some $$0 < \alpha < 1$$ selected for optimal returns. However, in order to enter a short trade on ETH-OVL, the investor must first sell half of her OVL for ETH on spot. Thus to balance the investor needs $$2 \alpha n$$, where half of this is actually being held in ETH.

Case 1a: After $$m$$ oracle fetches, someone else comees on the other side, partially the pool. Their trade triggers the

Case 1b: After $$m$$ oracle fetches, someone else comees on the other side, with OI greater than the current imbalance, creating a balance to the other wise. The imbalance is system then behaves as though the passive pool holders now switch their positions. When another transaction is made,

The tuple $$(\iota , \tau)$$ stands for imbalance, and time (be it block time, oracle fetch time, or what have you).

0. Some transaction on market is made at time $$t$$.  

1. Read $$(\iota, \tau)$$.

2. The passive pool is considered to have been trading the market alongside the $p$ traders, with size $$\alpha \iota$$. For example, $$\alpha = .33\$$. Compute the "virtual imbalance"  
\\[\\]

If $$\iota \neq 0$$, compute funding payments between $\tau$ and $$t$$. Say $$m$$ oracle fetches have occurred between $$\tau$$ and $$t$$. So the funding is
\\[ F = \iota (1-2k)^m\\]

3. Distribute $F$ pro rata between the $p$ traders as follows. Say $$\sum N_{ai} = P$$. Then we must have $$OI_{\hat{a}} - P = \iota$.


4. Funding is distributed among $p$ traders and the passive pool according to:
. , compute new $$(I, t)$$ and .   

1. If $$ I  \neq 0$$, then $$I$$ and update block (or oracle fetch number) are saved as attributes to market.

2. f




partially the pool. Their trade triggers the
Case 2:

No trades or transactions are made. The positions are "virtual" in the sense that by investing in the pool, the investors are agreeing to balance all open markets.

### Liquidation

The risk is that , thus caps can be set  

The rebalancings

### Example

Overlay has 1k active markets. Each of them are slightly unbalanced to the long side, but not enough for funding to pay for the fees to get in and out of the balancing trades.  

Overlay has 1 market that is *never* balanced. For whatever reason, nobody ever takes the other side.
