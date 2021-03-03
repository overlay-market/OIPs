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

### Portfolio Construction

Assume I have \\( n_{OVL} \\) total to trade with, and I want to take a position out on an Overlay market feed \\( X \\) while hedging out OVL price risk.

I stake an amount \\( q_{p} \cdot n_{OVL} \\) with leverage \\( l_p \\) on an Overlay market feed \\( X \\), where \\( 0 < q_{p} < 1 \\). I have an OVL amount \\( (1 - q_{p}) \cdot n_{OVL} \\) left to use for hedging to keep my PnL in ETH terms. For the purposes of this note, ignore [funding payments](note-1) between longs and shorts.

My payoff for the \\( X \\) feed position **in OVL terms** is

\\[ \mathrm{PO}\_p(t_n) = q_p \cdot n_{OVL} \cdot \bigg[ 1 + l_p \cdot (\pm)_{p} \cdot \bigg( \frac{P^X_n}{P^X_0} - 1 \bigg) \bigg] \\]

where \\( (\pm)\_{p} = 1 \\) if I took out a long and \\( (\pm)\_{p} = -1 \\) if I took out a short. \\( P^{X}_i \\) is the value of the \\( X \\) feed at time \\( t_i \\).

To hedge, I use the rest of my OVL to take out an additional short position with leverage \\( l_h \\) on the OVL-ETH market offered by the protocol. My payoff for this hedge **in OVL terms** is

\\[ \mathrm{PO}\_h(t_n) = (1-q_p) \cdot n_{OVL} \cdot \bigg[ 1 - l_h \cdot \bigg( \frac{P^{O/E}_n}{P^{O/E}_0} - 1 \bigg) \bigg] \\]

where \\( P^{O/E}_i \\) is the value of the OVL-ETH TWAP feed at time \\( t_i \\).

For simplicity's sake, assume the 1 hour TWAP for the OVL-ETH feed is approximately equal to the current spot OVL-ETH price. Then the value of my "portfolio" **in ETH terms** is

\\[ V(t_n) = P^{O/E}\_n \cdot \bigg( \mathrm{PO}\_p(t_n) + \mathrm{PO}\_h(t_n) \bigg) \\]

Total cost to construct the portfolio **in ETH terms**

\\[ C = P^{O/E}\_0 \cdot n_{OVL} \\]

and my PnL for the "portfolio" **in ETH terms** (\\( \mathrm{PnL} = V - C \\))

\\[ \mathrm{PnL}(t_n) = n_{OVL} \cdot \bigg[ P^{O/E}\_n \cdot \bigg( \mathrm{PO}\_p(t_n) + \mathrm{PO}\_h(t_n) \bigg) - P^{O/E}\_0 \bigg] \\]

We want to examine what happens to the PnL in ETH terms when the price of OVL v.s. ETH changes an amount \\( \epsilon_n \\). Take \\( P^{O/E}_n = P^{O/E}_0 \cdot (1 + \epsilon_n) \\) such that the OVL-ETH feed price has changed \\( \epsilon_n \\) from time \\( t_0 \\) to \\( t_n \\). PnL for the "portfolio" **in ETH terms** reduces to

\\[
\begin{eqnarray}
\mathrm{PnL}(t_n) = P^{O/E}\_0 \cdot n_{OVL} \cdot \bigg[ (1 + \epsilon_n) \cdot q_p \cdot l_p \cdot (\pm)_{p} \cdot \bigg(\frac{P^X_n}{P^X_0} - 1 \bigg) \\\\\\
\+ \epsilon\_n \cdot \bigg(1 - (1 - q\_{p}) \cdot l_h \bigg) \\\\\\
\- (1-q_p) \cdot l_h \cdot \epsilon^2_n \bigg]
\end{eqnarray}
\\]

where take \\( \epsilon_n \cdot ( P^X_n / P^X_0 - 1 ) \\) as second order. To eliminate first order terms, leverage for the hedge should be set to

\\[ l_h = \frac{1}{1-q_p} \\]

and then PnL **in ETH terms** becomes

\\[ \mathrm{PnL}(t_n) = P^{O/E}\_0 \cdot n_{OVL} \cdot \bigg[ (1 + \epsilon_n) \cdot q_p \cdot l_p \cdot (\pm)_{p} \cdot \bigg(\frac{P^X_n}{P^X_0} - 1 \bigg) - (1-q_p) \cdot l_h \cdot \epsilon^2_n \bigg] \\]

which to first order in price changes is \\( \mathrm{PnL}(t_n) \approx P^{O/E}\_0 \cdot n_{OVL} \cdot q_p \cdot l_p \cdot (\pm)_p \cdot (P^X_n / P^X_0 - 1) \\). Given the initial amount staked in the \\( X \\) feed position **in ETH terms** is \\( P^{O/E}\_0 \cdot q_p \cdot n\_{OVL}\\), PnL to first order for the "portfolio" grows/shrinks linearly with respect to price changes in the \\( X \\) feed and the initial ETH amount staked. The combination of positions is then hedged to first order.
