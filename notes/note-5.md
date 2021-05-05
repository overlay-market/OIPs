---
note: 5
oip-num: 1
title: Bookkeeping in Market Contracts
status: WIP
author: Michael Feldman (@mikeyrf), Adam Kay (@mcillkay)
discussions-to: oip-1
created: 2021-04-25
updated: N/A
---

Issue to address with this note:

- Outline the bookkeeping in Overlay market contracts for a peer-to-pool model with leverage and funding payments.


## Context

Overlay allows traders to express a view on a data stream without the need for traditional counterparties to take the other side of their trade. The system accomplishes this through a peer-to-pool model. Traders lock the settlement currency of the system (OVL) in Overlay market contract pools at a time \\( 0 \\) and, in exchange, receive a position token detailing the attributes of their trade (collateral, leverage, long/short, entry value). At some time \\( m > 0 \\) in the future when they wish to exit their position, traders can burn the position token through the market contract, and the market contract will compensate them for their profit or loss with more or less OVL than what they initially locked.

To compensate traders for a profitable trade when they exit their position, the market contract mints the amount of OVL associated with the realized profits to the circulating supply. The market contract then returns to the trader the initial OVL collateral locked plus the newly minted OVL.

Conversely, for an unprofitable trade, the market contract removes the amount of OVL associated with the realized losses from the circulating supply, by burning upon exit a portion of the initial OVL collateral locked. The market contract then returns to the trader an amount of OVL equal to the initial collateral locked minus the burnt losses.

A simple example, without leverage and [funding payments](note-1), to illustrate.

At time \\( 0 \\),

- Total circulating supply of OVL: 8,000,000 OVL. We have: 10 OVL

- We lock 10 OVL in a long position on the \\( X \\) feed for an entry market price of \\( x=100 \\)

At a future time \\( m \\),

- The \\( X \\) feed has gone up 20%. We take profits, unwinding our position at an exit price of \\( x=120 \\)

- The market contract mints an additional 2 OVL to the total circulating supply. It returns 12 OVL to us

- Total circulating supply of OVL: 8,000,002 OVL. We have: 12 OVL.

If the \\( X \\) feed had gone down 20% instead, the market contract would have burnt 2 OVL from the circulating supply and returned 8 OVL to us. The end state would have been a total circulating supply of 7,999,998 OVL and us having a balance of 8 OVL.

Things get more complex once we factor in leverage and funding with a peer-to-pool model. The purpose of this note is to outline the accounting with these dynamics in play.


## Dynamics with Leverage and Funding

Profit and loss for a market position \\( j \\) is determined by

\\[ \mathrm{PnL}\_{aj}(m) = \mathrm{OI}_{aj} (m) \cdot \bigg[ \frac{P(m)}{P(0)} - 1 \bigg] \\]

\\( P(t) \\) is the market value fetched from the oracle at time \\( t \\). \\( \mathrm{OI}_{aj} (t) \\) is position \\( j \\)'s contribution to the total open interest at time \\( t \\) on side \\( a \in \\{ l, s \\} \\), where \\( l \\) is long and \\( s \\) is short.

Upon initially locking in a position, the  \\( \mathrm{OI}\_{aji} (0) = N\_{aji} \cdot L\_{aj} \\)

If the notional on the long side of the market outweighs

The liquidity in this model comes from

The introduction of leverage and [funding payments](note-1) ...
