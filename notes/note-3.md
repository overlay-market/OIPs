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

Issue to address with this note:

- How do I hedge out my OVL price exposure when entering into a position on an Overlay market?


## Context

In order to take positions on markets offered by the protocol, traders need to lock the settlement currency of the system (OVL). For traders that don't want price exposure to OVL but still wish to take a position on a market, they should be able to construct a "portfolio" that hedges out OVL price risk with respect to a quote currency like ETH. Below, I'll address how to construct this type of portfolio as a combination of different positions on separate Overlay markets.

Assume our initial liquidity mining phase is successful, and we're able to bootstrap $20M+ in liquidity on spot markets for the OVL-ETH pair. A [manipulation-resistant TWAP](note-2) on ETH-OVL can then be offered as an additional market to trade on Overlay. There are significant benefits to this:

1. I can lever up on OVL price exposure using OVL on Overlay.

2. I can hedge away some price exposure to OVL on my other Overlay positions by longing the ETH-OVL feed (inverse market) with appropriate leverage.

The second point is key to understanding how we'll construct this "portfolio" of positions.


## Quanto

### Summary

To hedge out some price exposure to \\( q \cdot n \\) OVL locked in a market position (where \\( 0 < q < 1 \\)), enter into an additional long position of \\( (1-q) \cdot n \\) locked on the ETH-OVL market with leverage of \\( 1/(1-q) \\). It is an imperfect hedge given the quanto nature of the original market position.

### Portfolio Construction

Assume I have a total of \\( n \\) OVL to trade with, and I want to take a position out on an Overlay market feed \\( X \\) while hedging out OVL price risk.

I lock an OVL amount \\( q \cdot n \\) with leverage \\( l_X \\) on an Overlay market feed \\( X \\), where \\( 0 < q < 1 \\). I have an OVL amount \\( (1 - q) \cdot n \\) left to use for hedging to attempt to keep my PnL in ETH terms. For the purposes of this note, ignore [funding payments](note-1) between longs and shorts.

My payoff for the \\( X \\) feed position **in OVL terms** is

\\[ \mathrm{PO}\_{X}(t) = q \cdot n \cdot \bigg[ 1 + l_X (\pm)_{X} \cdot \bigg( \frac{P\_X(t)}{P_X(0)} - 1 \bigg) \bigg] \\]

where \\( (\pm)_{X} = 1 \\) if I took out a long on the \\( X \\) market and \\( (\pm)_X = -1 \\) if I took out a short. \\( P\_{X}(t) \\) is the value of the \\( X \\) feed \\( t \\) blocks after I lock in my position.

To attempt to hedge, I use the rest of my OVL to take out an additional short position with leverage \\( l \\) on the ETH-OVL market offered by the protocol. My payoff for this hedge **in OVL terms** is

\\[ \mathrm{PO}\_{EO} (t) = (1-q) \cdot n \cdot \bigg[ 1 + l \cdot \bigg( \frac{P(t)}{P(0)} - 1 \bigg) \bigg] \\]

where \\( P(t) \\) is the value of the ETH-OVL TWAP feed \\( t \\) blocks after I lock in my position (i.e. [number of OVL] / [number of ETH] on spot).

For simplicity's sake, assume the 1 hour TWAP for the ETH-OVL feed is approximately equal to the current spot ETH-OVL price. Then the value of my "portfolio" **in ETH terms** is

\\[ V (t) = \frac{1}{P(t)} \cdot \bigg( \mathrm{PO}\_{X} (t) + \mathrm{PO}\_{EO} (t) \bigg) \\]

Total cost to construct the portfolio **in ETH terms**

\\[ C = \frac{n}{P(0)} \\]

and my PnL for the "portfolio" **in ETH terms** (\\( \mathrm{PnL} = V - C \\))

\\[ \mathrm{PnL}(t) =  \frac{1}{P(t)} \cdot \bigg( \mathrm{PO}_X (t) + \mathrm{PO}\_{EO} (t) \bigg) - \frac{n}{P(0)} \\]

We want to examine what happens to the PnL in ETH terms when the price of ETH vs OVL changes an amount \\( \epsilon \\). Take \\( P(t) = P(0) \cdot (1 + \epsilon) \\) such that the ETH-OVL feed price has changed \\( \epsilon \\) from time \\( 0 \\) to \\( t \\). Similarly, assume \\( P_X(t) = P_X(0) \cdot (1 + \epsilon_X) \\) such that the \\( X \\) market price has changed \\( \epsilon_X \\) from time \\( 0 \\) to \\( t \\). PnL for the "portfolio" **in ETH terms** reduces to

\\[ \mathrm{PnL}(t) = \frac{n}{P(t)} \cdot \bigg[ (\pm)\_{X} \cdot q \cdot l\_{X} \cdot \epsilon\_{X} + \epsilon \cdot \bigg(l \cdot (1 - q) - 1 \bigg) \bigg] \\]

To partially eliminate \\( \epsilon \\) terms, set leverage for the hedge to

\\[ l = \frac{1}{1-q} \\]

Then PnL **in ETH terms** becomes

\\[ \mathrm{PnL}(t) = \frac{q \cdot n}{P(t)} \cdot (\pm)\_{X} \cdot l\_{X} \cdot \epsilon\_{X} \\]

Given the amount of collateral locked in the \\( X \\) feed position **in ETH terms** at time \\( t \\) is \\( \frac{q \cdot n}{P(t)} \\), PnL is partially hedged with respect to changes in ETH-OVL price. However, it still carries significant exposure for large changes in \\( \epsilon \\) through \\( P(t) \\), and so is a rather imperfect as a hedge.


### Concrete Numbers

We'll start with a relatively conservative case where prices only change a few percentage points to show the benefits of the hedge. Then, move on to a more extreme and likely case, showing why the hedge isn't great for more volatile scenarios.

Assume we have \\( n = 100 \\) OVL to trade with, and we decide to long the \\( X \\) feed with 80 OVL at 1x leverage for a \\( q = 0.8 \\). As we enter the position, take the price of OVL to be at parity with ETH such that 1 OVL = 1 ETH, so we're effectively locking 80 ETH worth of OVL on \\( X \\).

#### Case 1: \\(X \uparrow 10\% \\), \\(EO \uparrow 5\%\\)

Let's look at what happens to our PnL when:

 - The X feed increases 10%
 - But the ETH-OVL feed increases 5% (OVL becomes less valuable)

Begin with the unhedged long. Value of the position **in OVL terms** will be

\\[ V^X = 80 \cdot (1 + 0.1) = 88 \; \mathrm{OVL} \\]

but **in ETH terms** reduces to

\\[ V^X = 88 \; \mathrm{OVL} \cdot 0.95 \; \mathrm{ETH} / \mathrm{OVL} = 83.6 \; \mathrm{ETH} \\]

PnL is then the OVL equivalent of 3.6 ETH on the long, much smaller than the anticipated 8 ETH.

Now, add in the hedge with a \\( l^{OE} = 1/(1-q) = 5 \mathrm{x} \\) short on the OVL-ETH feed. Value of the hedge **in OVL terms** after OVL-ETH drops will be

\\[ V^{OE} = 20 \cdot (1 + 5 \cdot 0.05) = 25 \; \mathrm{OVL} \\]

which gives a total portfolio value **in ETH terms** of 107.35 ETH. Total PnL is then the OVL equivalent of 7.35 ETH on the combination, preserving most of the anticipated profit from the long. Sanity check by plugging into the expression for \\( \mathrm{PnL}_{k} \\) from the previous section works out.

#### Case 2: \\(X \uparrow 20\% \\), \\(EO \uparrow 25\%\\)

Similarly, what happens when:

 - The X feed increases 20%
 - But the ETH-OVL feed increases 25% (OVL becomes less valuable)

Unhedged long **in OVL terms**

\\[ V^X = 80 \cdot (1 + 0.2) = 96 \; \mathrm{OVL} \\]

becomes equivalent to \\( V^X = 72 \; \mathrm{ETH} \\). Meaning, we lost 8 ETH or 10% **in ETH terms**.

Combined with the hedge **in OVL terms**

\\[ V^{OE} = 20 \cdot (1 + 5 \cdot 0.25) = 45 \; \mathrm{OVL} \\]

gives a total portfolio value of \\( 141 \; \mathrm{OVL} = 105.75 \; \mathrm{ETH} \\) and profit equivalent to 5.75 ETH or 5.75% **in ETH terms**. Still better than unhedged, but profit has degraded substantially (the hedge is not that great).

Furthermore, a 5x short means it's easier to get liquidated if OVL-ETH moves counter to the hedge. \\( q \\) should be adjusted accordingly.
