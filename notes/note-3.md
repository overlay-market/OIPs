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

In order to take positions on markets offered by the protocol, traders need to stake the settlement currency of the system (OVL). For traders that don't want price exposure to OVL but still wish to take a position on a market, they should be able to construct a "portfolio" that hedges out OVL price risk with respect to a quote currency like ETH. Below, I'll address how to construct this type of portfolio as a combination of different positions on separate Overlay markets.

Assume our initial liquidity mining phase is successful, and we're able to bootstrap $20M+ in liquidity on spot markets for the OVL-ETH pair. A [manipulation-resistant TWAP](note-2) on OVL-ETH can then be offered as an additional market to trade on Overlay. There are significant benefits to this:

1. I can lever up long on OVL-ETH price exposure using OVL on Overlay.

2. I can hedge away some price exposure to OVL on my other Overlay positions by shorting with appropriate leverage the OVL-ETH feed.

The second point is key to understanding how we'll construct this "portfolio" of positions.


## Quanto

### Summary

To hedge out some price exposure to \\( q \cdot n \\) OVL staked in a market position (where \\( 0 < q < 1 \\)), enter into an additional short position of \\( (1-q) \cdot n \\) staked on the OVL-ETH market with leverage of \\( 1/(1-q) \\). It is an imperfect hedge given the quanto nature of the original market position, but will partially work to first order in price fluctuations on the OVL-ETH TWAP.

### Portfolio Construction

Assume I have a total of \\( n \\) OVL to trade with, and I want to take a position out on an Overlay market feed \\( X \\) while hedging out OVL price risk.

I stake an OVL amount \\( q \cdot n \\) with leverage \\( l^X \\) on an Overlay market feed \\( X \\), where \\( 0 < q < 1 \\). I have an OVL amount \\( (1 - q) \cdot n \\) left to use for hedging to keep my PnL in ETH terms. For the purposes of this note, ignore [funding payments](note-1) between longs and shorts.

My payoff for the \\( X \\) feed position **in OVL terms** is

\\[ \mathrm{PO}\_{k}^X = q \cdot n \cdot \bigg[ 1 + l^X \cdot (\pm)^{X} \cdot \bigg( \frac{P^X_k}{P^X_0} - 1 \bigg) \bigg] \\]

where \\( (\pm)^{X} = 1 \\) if I took out a long and \\( (\pm)^X = -1 \\) if I took out a short. \\( P^{X}_k = P^{X}(t_k) \\) is the value of the \\( X \\) feed at time \\( t_k \\), \\( k \\) blocks after I take my positions. \\( P^{X}_0 = P^{X}(t_0) \\) is the value of the feed that I lock in for my \\( X \\) market position when I build the "portfolio".

To attempt to hedge, I use the rest of my OVL to take out an additional short position with leverage \\( l^{OE} \\) on the OVL-ETH market offered by the protocol. My payoff for this hedge **in OVL terms** is

\\[ \mathrm{PO}\_{k}^{OE} = (1-q) \cdot n \cdot \bigg[ 1 - l^{OE} \cdot \bigg( \frac{P^{OE}_k}{P^{OE}_0} - 1 \bigg) \bigg] \\]

where \\( P^{OE}_k \\) is the value of the OVL-ETH TWAP feed at time \\( t_k \\).

For simplicity's sake, assume the 1 hour TWAP for the OVL-ETH feed is approximately equal to the current spot OVL-ETH price. Then the value of my "portfolio" **in ETH terms** is

\\[ V_k = P^{OE}\_k \cdot \bigg( \mathrm{PO}\_k^{X} + \mathrm{PO}\_k^{OE} \bigg) \\]

Total cost to construct the portfolio **in ETH terms**

\\[ C = P^{OE}\_0 \cdot n \\]

and my PnL for the "portfolio" **in ETH terms** (\\( \mathrm{PnL} = V - C \\))

\\[ \mathrm{PnL}\_k =  P^{OE}\_k \cdot \bigg( \mathrm{PO}^X_k + \mathrm{PO}\_k^{OE} \bigg) - P^{OE}\_0 \cdot n \\]

We want to examine what happens to the PnL in ETH terms when the price of OVL vs ETH changes an amount \\( \epsilon_k \\). Take \\( P^{OE}_k = P^{OE}_0 \cdot (1 + \epsilon_k) \\) such that the OVL-ETH feed price has changed \\( \epsilon_k \\) from time \\( t_0 \\) to \\( t_k \\). PnL for the "portfolio" **in ETH terms** reduces to

\\[
\begin{eqnarray}
\mathrm{PnL}\_k = P^{OE}\_0 \cdot n \cdot \bigg[ (1 + \epsilon_k) \cdot q \cdot l^X \cdot (\pm)^{X} \cdot \bigg(\frac{P^X_k}{P^X_0} - 1 \bigg) \\\\\\
\+ \epsilon\_k \cdot \bigg(1 - (1 - q) \cdot l^{OE} \bigg) \\\\\\
\- (1-q) \cdot l^{OE} \cdot \epsilon^2_k \bigg]
\end{eqnarray}
\\]

where take \\( \epsilon_k \cdot ( P^X_k / P^X_0 - 1 ) \\) as second order in price changes (albeit a strong assumption). To eliminate first order terms, set leverage for the hedge to

\\[ l^{OE} = \frac{1}{1-q} \\]

and then PnL **in ETH terms** becomes

\\[ \mathrm{PnL}\_k = P^{OE}\_0 \cdot n \cdot \bigg[ (1 + \epsilon_k) \cdot q \cdot l^X \cdot (\pm)^X \cdot \bigg(\frac{P^X_k}{P^X_k} - 1 \bigg) - \epsilon^2_k \bigg] \\]

Given the initial amount staked in the \\( X \\) feed position **in ETH terms** is \\( P^{OE}\_0 \cdot q \cdot n \\), PnL is partially hedged to first order in OVL-ETH price changes for the "portfolio". However, it still carries significant exposure for large changes in \\( \epsilon_k \\), and so is rather imperfect as a hedge.


### Concrete Numbers

We'll start with a relatively conservative case where prices only change a few percentage points to show the benefits of the hedge. Then, move on to a more extreme and likely case, showing why the hedge isn't great for more volatile scenarios.

Assume we have \\( n = 100 \\) OVL to trade with, and we decide to long the \\( X \\) feed with 80 OVL at 1x leverage for a \\( q = 0.8 \\). As we enter the position, take the price of OVL to be at parity with ETH such that 1 OVL = 1 ETH, so we're effectively staking 80 ETH worth of OVL on \\( X \\).

#### Case 1: \\(X \uparrow 10\% \\), \\(OE \downarrow 5\%\\)

Let's look at what happens to our PnL when:

 - The X feed increases 10%
 - But OVL-ETH decreases 5%

Begin with the unhedged long. Value of the position **in OVL terms** will be

\\[ V^X = 80 \cdot (1 + 0.1) = 88 \; \mathrm{OVL} \\]

but **in ETH terms** reduces to

\\[ V^X = 88 \; \mathrm{OVL} \cdot 0.95 \; \mathrm{ETH} / \mathrm{OVL} = 83.6 \; \mathrm{ETH} \\]

PnL is then the OVL equivalent of 3.6 ETH on the long, much smaller than the anticipated 8 ETH.

Now, add in the hedge with a \\( l^{OE} = 1/(1-q) = 5 \mathrm{x} \\) short on the OVL-ETH feed. Value of the hedge **in OVL terms** after OVL-ETH drops will be

\\[ V^{OE} = 20 \cdot (1 + 5 \cdot 0.05) = 25 \; \mathrm{OVL} \\]

which gives a total portfolio value **in ETH terms** of 107.35 ETH. Total PnL is then the OVL equivalent of 7.35 ETH on the combination, preserving most of the anticipated profit from the long.

#### Case 2: \\(X \uparrow 20\% \\), \\(OE \downarrow 25\%\\)

Similarly, what happens when:

 - The X feed increases 20%
 - But OVL-ETH decreases 25%

Unhedged long **in OVL terms**

\\[ V^X = 80 \cdot (1 + 0.2) = 96 \; \mathrm{OVL} \\]

becomes equivalent to \\( V^X = 72 \; \mathrm{ETH} \\). Meaning, we lost 8 ETH or 10% **in ETH terms**.

Combined with the hedge **in OVL terms**

\\[ V^{OE} = 20 \cdot (1 + 5 \cdot 0.25) = 45 \; \mathrm{OVL} \\]

gives a total portfolio value of \\( 141 \; \mathrm{OVL} = 105.75 \; \mathrm{ETH} \\) and profit equivalent to 5.75 ETH or 5.75% **in ETH terms**. Still better than unhedged, but profit has degraded substantially (the hedge is not that great).

Furthermore, a 5x short means it's easier to get liquidated if OVL-ETH moves counter to the hedge. \\( q \\) should be adjusted accordingly.
