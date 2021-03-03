---
note: 3
oip-num: 1
title: Hedging OVL Exposure
status: WIP
author: Michael Feldman (@mikeyrf)
discussions-to: oip-1
created: 2021-03-02
updated: N/A
---

Major issue to address with this note:

- How do I hedge out my OVL price exposure when entering into a position on an Overlay market?


## Context

In order to take positions on markets offered by the protocol, traders need to stake the settlement currency of the system (OVL). For traders that don't want price exposure to OVL but still wish to take a position on a market, they should be able to construct a "portfolio" that hedges out OVL price risk with respect to a quote currency like ETH. Below, I'll address how to construct this type of portfolio as a combination of different positions on separate Overlay markets.

Assume our initial liquidity mining phase is successful, and we're able to bootstrap $20M+ in liquidity on spot markets for the OVL-ETH pair. A [manipulation-resistant TWAP](note-2) on OVL-ETH can then be offered as an additional market to trade on Overlay. There are significant benefits to this:

1. I can lever up long on OVL-ETH price exposure using OVL on Overlay.

2. I can hedge away price exposure to OVL on my other Overlay positions by shorting with appropriate leverage the OVL-ETH feed.

The second point is key to understanding how we'll construct this "portfolio" of positions.


## Quanto

### Summary

To hedge out price exposure to \\( q_{p} \cdot n_{OVL} \\) OVL staked in a market position (where \\( 0 < q_{p} < 1 \\)), enter into an additional short position of \\( (1-q_{p}) \cdot n_{OVL} \\) staked on the OVL-ETH market with leverage of \\( 1/(1-q_{p}) \\). This will work to first order in price fluctuations on the OVL-ETH TWAP and be a partial hedge to second order.

### The Setup

I stake an amount \\( q_{p} \cdot n_{OVL} \\) with leverage \\( l_p \\) on an Overlay market \\( X \\) (where \\( 0 < q_{p} < 1 \\)). I have an OVL amount \\( (1 - q_{p}) \cdot n_{OVL} \\) left to hedge with so my PnL is in ETH terms. For the purposes of this note, ignore [funding payments](note-1) between longs and shorts.

My payoff for the \\( X \\) feed position **in OVL terms** is

\\[ \mathrm{PO}\_p(t_n) = n_{OVL} \cdot \bigg[ 1 - l_p \cdot (\pm)_{p} \cdot \bigg( \frac{P_n}{P_0} - 1 \bigg) \bigg] \\]

### Portfolio Construction
