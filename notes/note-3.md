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

- How do we hedge out OVL price exposure when entering into a position on an Overlay market?


## Context

In order to take positions on markets offered by the protocol, traders need to lock the settlement currency of the system (OVL). For traders that don't want price exposure to OVL but still wish to take a position on a market, they should be able to construct a "portfolio" that hedges out OVL price risk with respect to another currency like ETH. Below, I'll address how to construct this type of portfolio as a combination of different positions on separate Overlay markets.

Assume our initial liquidity mining phase is successful, and we're able to bootstrap $20M+ in liquidity on spot markets for the OVL-ETH pair. A [manipulation-resistant TWAP](note-2) on ETH-OVL can then be offered as an additional (inverse) market to trade on Overlay. There are significant benefits to this:

1. We can lever up on OVL price exposure using OVL on Overlay.

2. We can hedge away some price exposure to OVL on other Overlay positions by longing the ETH-OVL feed (units of OVL/ETH) with appropriate leverage.

The second point is key to understanding how we'll construct this "portfolio" of positions.


## Quanto

### Summary

To hedge out some price exposure to \\( q \cdot n \\) OVL locked in a market position (where \\( 0 < q < 1 \\)), enter into an additional long position of \\( (1-q) \cdot n \\) locked on the ETH-OVL market with leverage of \\( 1/(1-q) \\). It is an imperfect hedge given the quanto nature of the original market position.

### Portfolio Construction

Assume we have a total of \\( n \\) OVL to trade with, and we want to take a position out on an Overlay market feed \\( X \\) while hedging out OVL price risk.

We lock an OVL amount \\( q \cdot n \\) with leverage \\( l_X \\) on an Overlay market feed \\( X \\), where \\( 0 < q < 1 \\). We have an OVL amount \\( (1 - q) \cdot n \\) left to use for hedging to attempt to keep PnL in ETH terms. For the purposes of this note, ignore [funding payments](note-1) between longs and shorts.

Payoff for the \\( X \\) feed position **in OVL terms** is

\\[ \mathrm{PO}\_{X}(t) = q \cdot n \cdot \bigg[ 1 + l_X (\pm)_{X} \cdot \bigg( \frac{P\_X(t)}{P_X(0)} - 1 \bigg) \bigg] \\]

where \\( (\pm)_{X} = 1 \\) if we took out a long on the \\( X \\) market and \\( (\pm)_X = -1 \\) if we took out a short. \\( P\_{X}(t) \\) is the value of the \\( X \\) feed \\( t \\) blocks after we lock in our position.

To attempt to hedge, we use the rest of our OVL to take out an additional short position with leverage \\( l \\) on the ETH-OVL market offered by the protocol. Payoff for this hedge **in OVL terms** is

\\[ \mathrm{PO}\_{EO} (t) = (1-q) \cdot n \cdot \bigg[ 1 + l \cdot \bigg( \frac{P(t)}{P(0)} - 1 \bigg) \bigg] \\]

where \\( P(t) \\) is the value of the ETH-OVL TWAP feed \\( t \\) blocks after we lock in our position (i.e. [number of OVL] / [number of ETH] on spot).

For simplicity's sake, assume the 1 hour TWAP for the ETH-OVL feed is approximately equal to the current spot ETH-OVL price. Then the value of our "portfolio" **in ETH terms** is

\\[ V (t) = \frac{1}{P(t)} \cdot \bigg[ \mathrm{PO}\_{X} (t) + \mathrm{PO}\_{EO} (t) \bigg] \\]

Total cost to construct the portfolio **in ETH terms**

\\[ C = \frac{n}{P(0)} \\]

and PnL for the "portfolio" **in ETH terms** (\\( \mathrm{PnL} = V - C \\))

\\[ \mathrm{PnL}(t) =  \frac{1}{P(t)} \cdot \bigg[ \mathrm{PO}_X (t) + \mathrm{PO}\_{EO} (t) \bigg] - \frac{n}{P(0)} \\]

Examine what happens to the PnL in ETH terms when the price of ETH vs OVL changes. Take \\( P(t) = P(0) \cdot (1 + \epsilon) \\) such that the ETH-OVL feed price has changed \\( \epsilon \\) from time \\( 0 \\) to \\( t \\). Similarly, assume \\( P_X(t) = P_X(0) \cdot (1 + \epsilon_X) \\) such that the \\( X \\) feed has changed \\( \epsilon_X \\) from time \\( 0 \\) to \\( t \\). PnL for the "portfolio" **in ETH terms** reduces to

\\[ \mathrm{PnL}(t) = \frac{n}{P(t)} \cdot \bigg[ (\pm)\_{X} \cdot q \cdot l\_{X} \cdot \epsilon\_{X} + \epsilon \cdot \bigg(l \cdot (1 - q) - 1 \bigg) \bigg] \\]

To partially eliminate \\( \epsilon \\) terms, set leverage for the hedge to

\\[ l = \frac{1}{1-q} \\]

Then PnL **in ETH terms** becomes

\\[ \mathrm{PnL}(t) = \frac{q \cdot n}{P(t)} \cdot (\pm)\_{X} \cdot l\_{X} \cdot \epsilon\_{X} \\]

Given the amount of collateral locked in the \\( X \\) feed position **in ETH terms** at time \\( t \\) is \\( \frac{q \cdot n}{P(t)} \\), PnL is partially hedged with respect to changes in ETH-OVL price. However, it still carries significant exposure for large changes in \\( \epsilon \\) through \\( P(t) \\), and so is rather imperfect as a hedge.

Further, relative to the ETH PnL we wish to replicate, \\( \frac{n}{P(0)} \cdot (\pm)\_{X} \cdot l\_{X} \cdot \epsilon\_{X} \\), our PnL is scaled downward based on the proportion of capital \\( q \\) we choose to use in the \\( X \\) position vs the hedge. The less capital we lock in the hedge (i.e. \\( q \to 1 \\), \\( l \to \infty \\)), the more the hedged portfolio mimics the ETH PnL structure we desire. However, the more we increase our leverage on the hedge, the more we need to worry about the hedge getting liquidated.


### Unhedged vs Hedged

Compare the difference in PnL between the hedged and unhedged portfolios. For unhedged, simply take \\( q \to 1 \\) in the expressions above to obtain \\( \mathrm{PnL}\|\_{u}(t) = \frac{n}{P(t)} \cdot [ (\pm)_X \cdot l_X \cdot \epsilon\_X - \epsilon ] \\). Hedged is our expression above: \\( \mathrm{PnL}\|\_{h}(t) = \frac{q \cdot n}{P(t)} \cdot (\pm)_X \cdot l_X \cdot \epsilon\_X \\). Thus,

\\[ \mathrm{PnL}\|\_{u}(t) - \mathrm{PnL}\|\_{h}(t) = \frac{n}{P(t)} \cdot \bigg[ (1-q) \cdot (\pm)_X \cdot l_X \cdot \epsilon\_X - \epsilon \bigg] \\]

The less capital we lock in the hedge, the more the difference in PnL between the unhedged and hedged portfolios reduces to the linear price exposure to ETH-OVL feed, \\( \epsilon \\), we wish to hedge out.

When does the hedge pay off? The condition for the hedge to preserve more ETH profit, \\( \mathrm{PnL}\|\_{u} < \mathrm{PnL}\|\_{h} \\), occurs when

\\[ (1 - q) \cdot (\pm)_{X} \cdot l_X \cdot \epsilon\_X - \epsilon < 0 \\]

or when the ETH-OVL price feed increases

\\[ \epsilon > \frac{l_X}{l} \cdot (\pm)_X \cdot \epsilon_X \\]

where we've used \\( l = \frac{1}{1-q} \\) for the hedge.

### Concrete Numbers

We'll start with a relatively conservative case where prices only change a few percentage points to show the benefits of the hedge. Then, move on to a more extreme and likely case, showing why the hedge isn't great for more volatile scenarios.

Assume we have \\( n = 100 \\) OVL to trade with, and we decide to long the \\( X \\) feed with 80 OVL at 1x leverage for a \\( q = 0.8 \\). As we enter the position, take the price of OVL to be at parity with ETH such that 1 OVL = 1 ETH, so we're effectively locking 80 ETH worth of OVL on \\( X \\).

#### Case 1: \\(X \uparrow 10\% \\), \\(EO \uparrow 5\%\\)

Let's look at what happens to our PnL when:

 - The X feed increases 10%
 - But the ETH-OVL feed increases 5% (OVL becomes less valuable)

*Unhedged X Position:*

Begin with the unhedged long for comparison, locking all 100 OVL on the X feed. Value of the position **in OVL terms** will be

\\[ V = 100 \cdot (1 + 0.1) = 110 \; \mathrm{OVL} \\]

but **in ETH terms** reduces to

\\[ V = 110 \; \mathrm{OVL} / ( 1.05 \; \mathrm{OVL} / \mathrm{ETH} ) = 104.76 \; \mathrm{ETH} \\]

PnL is then the OVL equivalent of 4.76 ETH on the long.

The 10% gain from the \\( X \\) feed position has been reduced to a 4.76% gain in ETH terms. Summarizing for the unhedged portfolio:

- 10% gain from the X feed
- ETH-OVL increased 5%
- **PnL of +4.76%** in ETH terms

*Hedged X Position:*

Now, add in the hedge with a \\( l = 1/(1-q) = 5 \mathrm{x} \\) long on the ETH-OVL feed. Value of the portfolio **in OVL terms** after ETH-OVL increases will be

\\[ V = 80 \cdot (1 + 0.1) + 20 \cdot (1 + 5 \cdot 0.05) = 113 \; \mathrm{OVL} \\]

but **in ETH terms** reduces to

\\[ V = 113 \; \mathrm{OVL} / ( 1.05 \; \mathrm{OVL} / \mathrm{ETH} ) = 107.62 \; \mathrm{ETH} \\]

Total PnL is then the OVL equivalent of 7.62 ETH on the combination.

The 10% gain from the X feed position has been reduced to a gain of 7.62% in ETH terms, so the hedge protects a substantial portion of the gains. Summarizing for the hedged portfolio:

- 10% gain from the X feed
- ETH-OVL increased 5%
- **PnL of +7.62%** in ETH terms

Sanity check by plugging into the expression for hedged portfolio \\( \mathrm{PnL}(t) = \frac{q \cdot n}{P(t)} \cdot (\pm)\_{X} \cdot l\_{X} \cdot \epsilon\_{X} \\) works out.

#### Case 2: \\(X \uparrow 20\% \\), \\(EO \uparrow 25\%\\)

Similarly, what happens when:

 - The X feed increases 20%
 - But the ETH-OVL feed increases 25% (OVL becomes less valuable)

 *Unhedged X Position:*

 Begin with the unhedged long for comparison, locking all 100 OVL on the X feed. Value of the position **in OVL terms** will be

 \\[ V = 100 \cdot (1 + 0.2) = 120 \; \mathrm{OVL} \\]

 but **in ETH terms** reduces to

 \\[ V = 120 \; \mathrm{OVL} / ( 1.25 \; \mathrm{OVL} / \mathrm{ETH} ) = 96 \; \mathrm{ETH} \\]

 PnL is then the OVL equivalent of -4 ETH on the long.

 The 20% gain from the \\( X \\) feed position has been reduced to a 4% *loss* in ETH terms. Summarizing for the unhedged portfolio:

 - 20% gain from the X feed
 - ETH-OVL increased 25%
 - **PnL of -4%** in ETH terms

 *Hedged X Position:*

 Now, add in the hedge with a \\( l = 1/(1-q) = 5 \mathrm{x} \\) long on the ETH-OVL feed. Value of the portfolio **in OVL terms** after ETH-OVL increases will be

 \\[ V = 80 \cdot (1 + 0.2) + 20 \cdot (1 + 5 \cdot 0.25) = 141 \; \mathrm{OVL} \\]

 but **in ETH terms** reduces to

 \\[ V = 141 \; \mathrm{OVL} / ( 1.25 \; \mathrm{OVL} / \mathrm{ETH} ) = 112.8 \; \mathrm{ETH} \\]

 Total PnL is then the OVL equivalent of 12.8 ETH on the combination.

 The 20% gain from the X feed position has been reduced to a gain of 12.8% in ETH terms, so the hedge protects a substantial portion of the gains. Instead of losing money on the unhedged position, we maintain a significant profit with the hedge. Summarizing for the hedged portfolio:

 - 20% gain from the X feed
 - ETH-OVL increased 25%
 - **PnL of +12.8%** in ETH terms

 Sanity check by plugging into the expression for hedged portfolio \\( \mathrm{PnL}(t) = \frac{q \cdot n}{P(t)} \cdot (\pm)\_{X} \cdot l\_{X} \cdot \epsilon\_{X} \\) works out.
