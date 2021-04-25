---
note: 3
oip-num: 1
title: Hedging OVL Exposure
status: WIP
author: Michael Feldman (@mikeyrf), Adam Kay (@mcillkay)
discussions-to: oip-1
created: 2021-03-02
updated: N/A
---

Issue to address with this note:

- How do we hedge out OVL price exposure when entering into a position on an Overlay market?


## Context

In order to take positions on markets offered by the protocol, traders need to lock the settlement currency of the system (OVL). For traders that don't want price exposure to OVL but still wish to take a position on a market, they should be able to construct a "portfolio" that hedges out OVL price risk with respect to another currency like ETH. Below, we address how to construct this type of portfolio as a combination of different positions on separate Overlay markets.

Assume our initial liquidity mining phase is successful, and we're able to bootstrap $20M+ in liquidity on spot markets for the OVL-ETH pair. A [manipulation-resistant TWAP](note-2) on ETH-OVL can then be offered as an additional (inverse) market to trade on Overlay. There are significant benefits to this:

1. We can lever up on OVL price exposure using OVL on Overlay.

2. We can hedge away some price exposure to OVL on other Overlay positions by longing the ETH-OVL feed (units of OVL/ETH) with appropriate leverage.

The second point is key to understanding how we'll construct this "portfolio" of positions.


## Quanto

### Summary

To hedge out some price exposure to \\( n q \\) OVL locked in a market position (where \\( 0 < q < 1 \\)), enter into an additional long position of \\( n (1-q) \\) locked on the ETH-OVL market with leverage of \\( 1/(1-q) \\). This is not handled by the contract -- the trader must do this manually. It is an imperfect hedge given the quanto nature of the original market position.

### Portfolio Construction

Assume we have a total of \\( n \\) OVL to trade with, and we want to take a position out on an Overlay market feed \\( X \\) while hedging out OVL price risk.

We lock an OVL amount \\( n q \\) with leverage \\( l_X \\) on the \\( X \\) market, where \\( 0 < q < 1 \\). We have an OVL amount \\( n (1 - q) \\) left to use for hedging out some OVL price exposure.

For this note, ignore [funding payments](note-1) between longs and shorts, and, for simplicity's sake, assume the 1 hour TWAP for the ETH-OVL feed is approximately equal to the current spot ETH-OVL price. Payoff, "portfolio" value, and PnL functions are **in ETH terms** given we care about making more ETH if we're looking to hedge out OVL exposure.

We will write $$P_E$$ and $$P_X$$ for the price of the ETH-OVL and X feeds, respectively. Payoff \\( \mathrm{PO}\_{X} \\) for the \\( X \\) feed position is

\\[ \mathrm{PO}\_{X}(t) = \frac{n q}{P_E(t)} \bigg[  (\pm)\_{X} \cdot l_X  \bigg( \frac{P\_X(t)}{P_X(0)} - 1 \bigg)  + 1 \bigg] \\]

where \\( (\pm)\_{X} = 1 \\) if we took out a long on the \\( X \\) market and \\( (\pm)\_X = -1 \\) if we took out a short. \\( P\_{X}(t) \\) is the value of the \\( X \\) feed \\( t \\) blocks after we lock in our position. \\( P\_{E}(t) \\) is the value of the ETH-OVL TWAP feed \\( t \\) blocks after we lock in our position (units of OVL/ETH).

To attempt to hedge, we use the rest of our OVL to take out an additional long position with leverage \\( l_E\\) on the ETH-OVL market offered by the protocol (long since it is an inverse market). Payoff \\( \mathrm{PO}\_{E} \\) for this hedge is

\\[ \mathrm{PO}\_{E} (t) = \frac{n (1-q)}{P_E(t)} \bigg[ l_E \bigg( \frac{P_E(t)}{P_E(0)} - 1 \bigg) + 1 \bigg] \\]

and the value of our entire "portfolio" is

\\[ V (t) = \mathrm{PO}\_{X} (t) + \mathrm{PO}\_{E} (t) \\]

Total cost to construct the portfolio

\\[ C = \frac{n}{P_E(0)} \\]

and PnL for the "portfolio"

\\[ \mathrm{PnL}(t) = V(t) - C \\]

Examine what happens to the PnL in ETH terms when the price of ETH vs OVL changes. Take \\( P\_{E}(t) = P\_{E}(0) (1 + \epsilon\_{E}) \\) such that the ETH-OVL feed changes an amount \\( \epsilon\_{E} \\) from time \\( 0 \\) to \\( t \\). Similarly, assume \\( P_X(t) = P_X(0) (1 + \epsilon_X) \\) such that the \\( X \\) feed changes an amount \\( \epsilon_X \\) from time \\( 0 \\) to \\( t \\). PnL for the "portfolio" reduces to

\\[ \mathrm{PnL}(t) = \frac{n}{P_E(t)} \bigg[ (\pm)\_{X} \cdot l\_{X} \epsilon\_{X} q + \epsilon\_{E} \bigg(l_E (1 - q) - 1 \bigg) \bigg] \\]

To partially eliminate \\( \epsilon\_{E} \\) terms, set leverage for the hedge to

\\[ l_E = \frac{1}{1-q} \\]

PnL becomes

\\[ \mathrm{PnL}(t) = (\pm)\_{X} \cdot \frac{n q}{P_E(t)} l\_{X} \epsilon\_{X} \\]

Given the amount of collateral locked in the \\( X \\) feed position **in ETH terms** at time \\( t \\) is \\( \frac{n q}{P_E(t)} \\), PnL is partially hedged with respect to changes in ETH-OVL price. However, it still carries significant exposure for large changes in \\( \epsilon \\) through \\( P_E(t) \\), and so is rather imperfect as a hedge. In other words, PnL still scales based on the value of the locked OVL collateral in ETH terms at the current time \\( t \\), \\( \frac{n q}{P_E(t)} \\), and not \\( \frac{n q}{P_E(0)} \\) as we would prefer.

Compared to the ETH PnL we wish to replicate, \\( \frac{(\pm)\_{X} \cdot n l\_{X} \epsilon\_{X}}{P_E(0)} \\), our PnL is also scaled downward based on the proportion of capital \\( q \\) we choose to use in the \\( X \\) position vs the hedge. The less capital we lock in the hedge (i.e. \\( q \to 1 \\), \\( l \to \infty \\)), the more the hedged portfolio mimics the ETH PnL structure we desire. However, the more we increase our leverage on the hedge, the more we need to worry about the hedge getting liquidated.


### Concrete Numbers

We'll start with a relatively conservative case where prices only change a few percentage points to show the benefits of the hedge. Then, move on to a more extreme and likely case, showing why the hedge becomes even more important.

Assume we have \\( n = 100 \\) OVL to trade with, and we decide to long the \\( X \\) feed at 1x leverage.  Further, take the price of OVL to be at parity with ETH such that 1 OVL = 1 ETH.

#### Case 1: \\(X \uparrow 10\% \\), \\(E \uparrow 5\%\\)

Let's look at what happens to our PnL when:

 - The X feed increases 10%
 - But the ETH-OVL feed increases 5% (OVL becomes less valuable)

*Unhedged X Position:*

Begin with the unhedged long for comparison, locking all 100 OVL on the X feed. Value of the position in OVL terms will be

\\[ V = 100 \cdot (1 + 0.1) = 110 \; \mathrm{OVL} \\]

but in ETH terms reduces to

\\[ V = 110 \; \mathrm{OVL} / ( 1.05 \; \mathrm{OVL} / \mathrm{ETH} ) = 104.76 \; \mathrm{ETH} \\]

as ETH-OVL increases 5%. Given we initially had 100 ETH, PnL is then the OVL equivalent of 4.76 ETH on the long.

The 10% gain from the \\( X \\) feed position has been reduced to a 4.76% gain in ETH terms.

Summarizing for the unhedged portfolio:

- 10% gain from the X feed
- ETH-OVL increased 5%
- **PnL of +4.76%** in ETH terms

*Hedged X Position:*

Now, add in the hedge with a \\( l = 1/(1-q) = 5 \mathrm{x} \\) long on the ETH-OVL feed. Value of the portfolio in OVL terms after ETH-OVL increases will be

\\[ V = 80 \cdot (1 + 0.1) + 20 \cdot (1 + 5 \cdot 0.05) = 113 \; \mathrm{OVL} \\]

but in ETH terms reduces to

\\[ V = 113 \; \mathrm{OVL} / ( 1.05 \; \mathrm{OVL} / \mathrm{ETH} ) = 107.62 \; \mathrm{ETH} \\]

as ETH-OVL increases 5%. Given we initially had 100 ETH, PnL is then the OVL equivalent of 7.62 ETH on the combination.

The 10% gain from the X feed position has been reduced to a gain of 7.62% in ETH terms, so the hedge protects a substantial portion of the gains.

Summarizing for the hedged portfolio:

- 10% gain from the X feed
- ETH-OVL increased 5%
- **PnL of +7.62%** in ETH terms

Sanity check by plugging into the expression for the hedged portfolio \\( \mathrm{PnL}(t) = (\pm)\_{X} \frac{n q}{P(t)} l\_{X} \epsilon\_{X} \\)

\\[ \mathrm{PnL}(t) = \frac{80 \; \mathrm{OVL}}{1.05 \; \mathrm{OVL}/\mathrm{ETH}} \cdot 1 \cdot 1 \cdot 0.10 = 7.62 \; \mathrm{ETH} \\]

works out.

#### Case 2: \\(X \uparrow 20\% \\), \\(E \uparrow 25\%\\)

Similarly, what happens when:

- The X feed increases 20%
- But the ETH-OVL feed increases 25% (OVL becomes less valuable)

*Unhedged X Position:*

Begin with the unhedged long for comparison, locking all 100 OVL on the X feed. Value of the position in OVL terms will be

\\[ V = 100 \cdot (1 + 0.2) = 120 \; \mathrm{OVL} \\]

but in ETH terms reduces to

\\[ V = 120 \; \mathrm{OVL} / ( 1.25 \; \mathrm{OVL} / \mathrm{ETH} ) = 96 \; \mathrm{ETH} \\]

as ETH-OVL increases 25%. Given we initially had 100 ETH, PnL is then the OVL equivalent of -4 ETH on the long.

The 20% gain from the \\( X \\) feed position has been reduced to a 4% *loss* in ETH terms.

Summarizing for the unhedged portfolio:

- 20% gain from the X feed
- ETH-OVL increased 25%
- **PnL of -4%** in ETH terms

*Hedged X Position:*

Now, add in the hedge with a \\( l = 1/(1-q) = 5 \mathrm{x} \\) long on the ETH-OVL feed. Value of the portfolio in OVL terms after ETH-OVL increases will be

\\[ V = 80 \cdot (1 + 0.2) + 20 \cdot (1 + 5 \cdot 0.25) = 141 \; \mathrm{OVL} \\]

but in ETH terms reduces to

\\[ V = 141 \; \mathrm{OVL} / ( 1.25 \; \mathrm{OVL} / \mathrm{ETH} ) = 112.8 \; \mathrm{ETH} \\]

as ETH-OVL increases 25%. Given we initially had 100 ETH, PnL is then the OVL equivalent of 12.8 ETH on the combination.

The 20% gain from the X feed position has been reduced to a *gain* of 12.8% in ETH terms. Compared to the loss without the hedge, the hedged portfolio protects a substantial portion of the gains. Instead of losing money on the unhedged position, we maintain a significant profit with the hedge.

Summarizing for the hedged portfolio:

- 20% gain from the X feed
- ETH-OVL increased 25%
- **PnL of +12.8%** in ETH terms

Sanity check by plugging into the expression for hedged portfolio \\( \mathrm{PnL}(t) = (\pm)\_{X} \frac{n q}{P(t)} l\_{X} \epsilon\_{X} \\)

\\[ \mathrm{PnL}(t) = \frac{80 \; \mathrm{OVL}}{1.25 \; \mathrm{OVL}/\mathrm{ETH}} \cdot 1 \cdot 1 \cdot 0.20 = 12.8 \; \mathrm{ETH} \\]

works out.

#### Breakdown

Profit/loss in ETH terms for both cases are summarized below.

\\(X \uparrow 10\% \\), \\(E \uparrow 5\%\\)

- Unhedged: PnL = +4.76%
- Hedged: PnL = +7.62%

\\(X \uparrow 20\% \\), \\(E \uparrow 25\%\\)

- Unhedged: PnL = -4%
- Hedged: PnL = +12.8%

Clearly the hedge helps, particularly for extreme volatility in ETH-OVL price, which seems likely at least to begin with. More examples with leverage on the \\( X \\) market position are in the [repo](https://github.com/overlay-market/OIPs/blob/master/_examples/oip-1/hedge.md).


## A Full Hedge

In fact, there is a way to get a full hedge by using *dynamic* leverage. It is done as follows. Expanding terms explicilty in the PnL formula we get

\\[ \mathrm{PnL}(t) = \frac{n}{P_E(0)} \bigg[ \frac{ (\pm)\_{X} \cdot q l\_{X} \epsilon\_{X} + \epsilon\_{E} (l_E (1 - q) - 1) }{1 + \epsilon_E}\bigg] \\]

from which it follows that if \\(l_E (1 - q) - 1 = (\pm)\_X \cdot q l\_{X} \epsilon\_{X}\\), then we will get

\\[ \mathrm{PnL}(t) = (\pm)\_{X} \frac{nq}{P_E(0)} l\_{X} \epsilon\_{X} \\]

a fully hedged position.

Let's write \\( (\pm)\_{X} l_X = \lambda\\), and $$\epsilon_X = x$$. The condition for the full hedge gives

\\[q = \frac{l_E - 1}{\lambda x + l_E}.
\\]

This value of $$q$$ changes as $$x$$ changes. As the position goes further onside, the denominator grows and $$q$$ decreases. This is an undesirable UX. Instead, we would prefer that $$q$$ is constant with price changes and that the hedging leverage $$l_E$$ changes as a function of $$x$$. The condition for this to happen is:

\\[ l\_{E}(x) = \frac{q \lambda x + 1}{1-q} \\]

This shows that we have essentially linear scaling of leverage with price movement, with initial leverage value $$\frac{1}{1-q}$$. As the position goes offside the required leverage to hedge decreases, whereas when it goes onside the leverage increases.


### Example

For a desired value of $$q$$, we can compute initial leverage easily

\\[l_E = \frac{1}{1-q}\\]

For a completely unleveraged long position on the $$X$$ market, we have $$\lambda x = \epsilon_X$$, and for $$q = \frac{1}{2}$$, we must initially set our hedging leverage to 2, which sets $$A= 1$$. Our leverage then scales dynamically as

\\[l_E = \epsilon_X + 2\\]

If we double our money on the $$X$$ market, our leverage on ETH-OVL goes from 2 to 3.
