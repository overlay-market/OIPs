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

Assume our initial liquidity mining phase is successful, and we're able to bootstrap $20M+ in liquidity on spot markets for the OVL/ETH pair. A [manipulation-resistant TWAP](note-2) on OVL/ETH can then be offered as an additional market to trade on Overlay. There are significant benefits to this:

1. I can lever up long on OVL/ETH price exposure using OVL on Overlay.

2. I can hedge away some price exposure to OVL on my other Overlay positions by shorting with appropriate leverage the OVL/ETH feed.

The second point is key to understanding how we'll construct this "portfolio" of positions.


## Quanto

### Summary

To hedge out some price exposure to \\( q \cdot n \\) OVL staked in a market position (where \\( 0 < q < 1 \\)), enter into an additional short position of \\( (1-q) \cdot n \\) staked on the OVL/ETH market with leverage of \\( 1/(1-q) \\). It is an imperfect hedge given the quanto nature of the original market position, but will partially work to first order in price fluctuations on the OVL/ETH TWAP.

### Portfolio Construction

Assume I have a total of \\( n \\) OVL to trade with, and I want to take a position out on an Overlay market feed \\( X \\) while hedging out OVL price risk.

I stake an OVL amount \\( q \cdot n \\) with leverage \\( l_X \\) on an Overlay market feed \\( X \\), where \\( 0 < q < 1 \\). I have an OVL amount \\( (1 - q) \cdot n \\) left to use for hedging to keep my PnL in ETH terms. For the purposes of this note, ignore [funding payments](note-1) between longs and shorts.

My payoff for the \\( X \\) feed position **in OVL terms** is

\\[ \mathrm{PO}\_{k}^X = q \cdot n \cdot \bigg[ 1 + l^X \cdot (\pm)^{X} \cdot \bigg( \frac{P^X_k}{P^X_0} - 1 \bigg) \bigg] \\]

where \\( (\pm)^{X} = 1 \\) if I took out a long and \\( (\pm)^X = -1 \\) if I took out a short. \\( P^{X}_k = P^{X}(t_k) \\) is the value of the \\( X \\) feed at time \\( t_k \\), \\( k \\) blocks after I take my positions. \\( P^{X}_0 = P^{X}(t_0) \\) is the value of the feed that I lock in for my \\( X \\) market position when I build the "portfolio".

To attempt to hedge, I use the rest of my OVL to take out an additional short position with leverage \\( l^{O/E} \\) on the OVL/ETH market offered by the protocol. My payoff for this hedge **in OVL terms** is

\\[ \mathrm{PO}\_{k}^{O/E} = (1-q) \cdot n \cdot \bigg[ 1 - l^{O/E} \cdot \bigg( \frac{P^{O/E}_k}{P^{O/E}_0} - 1 \bigg) \bigg] \\]

where \\( P^{O/E}_k \\) is the value of the OVL/ETH TWAP feed at time \\( t_k \\).

For simplicity's sake, assume the 1 hour TWAP for the OVL/ETH feed is approximately equal to the current spot OVL/ETH price. Then the value of my "portfolio" **in ETH terms** is

\\[ V_k = P^{O/E}\_k \cdot \bigg( \mathrm{PO}\_k^{X} + \mathrm{PO}\_k^{O/E} \bigg) \\]

Total cost to construct the portfolio **in ETH terms**

\\[ C = P^{O/E}\_0 \cdot n \\]

and my PnL for the "portfolio" **in ETH terms** (\\( \mathrm{PnL} = V - C \\))

\\[ \mathrm{PnL}\_k =  P^{O/E}\_k \cdot \bigg( \mathrm{PO}^X_k + \mathrm{PO}\_k^{O/E} \bigg) - P^{O/E}\_0 \cdot n \\]

We want to examine what happens to the PnL in ETH terms when the price of OVL vs ETH changes an amount \\( \epsilon_k \\). Take \\( P^{O/E}_k = P^{O/E}_0 \cdot (1 + \epsilon_k) \\) such that the OVL/ETH feed price has changed \\( \epsilon_k \\) from time \\( t_0 \\) to \\( t_k \\). PnL for the "portfolio" **in ETH terms** reduces to

\\[
\begin{eqnarray}
\mathrm{PnL}\_k = P^{O/E}\_0 \cdot n \cdot \bigg[ (1 + \epsilon_k) \cdot q \cdot l^X \cdot (\pm)^{X} \cdot \bigg(\frac{P^X_k}{P^X_0} - 1 \bigg) \\\\\\
\+ \epsilon\_k \cdot \bigg(1 - (1 - q) \cdot l^{O/E} \bigg) \\\\\\
\- (1-q) \cdot l^{O/E} \cdot \epsilon^2_k \bigg]
\end{eqnarray}
\\]

where take \\( \epsilon_k \cdot ( P^X_k / P^X_0 - 1 ) \\) as second order in price changes. To eliminate first order terms, leverage for the hedge should be set to

\\[ l^{O/E} = \frac{1}{1-q} \\]

and then PnL **in ETH terms** becomes

\\[ \mathrm{PnL}\_k = P^{O/E}\_0 \cdot n \cdot \bigg[ (1 + \epsilon_k) \cdot q \cdot l^X \cdot (\pm)^X \cdot \bigg(\frac{P^X_k}{P^X_k} - 1 \bigg) - \epsilon^2_k \bigg] \\]

Given the initial amount staked in the \\( X \\) feed position **in ETH terms** is \\( P^{O/E}\_0 \cdot q \cdot n \\), PnL is partially hedged to first order in OVL/ETH price changes for the "portfolio". However, it still carries significant exposure for large changes in \\( \epsilon_k \\), and so is rather imperfect as a hedge.
