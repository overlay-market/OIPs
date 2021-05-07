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

Overlay allows traders to express a view on a data stream without the need for traditional counterparties to take the other side of their trade. The system accomplishes this through a peer-to-pool model. Traders lock the settlement currency of the system (OVL) in Overlay market contract pools at a time \\( 0 \\) and, in exchange, receive a position token detailing the attributes of their trade (collateral, leverage, long/short, entry value). At some time \\( t > 0 \\) in the future when they wish to exit their position, traders can burn the position token through the market contract, and the market contract will compensate them for their profit or loss with more or less OVL than what they initially locked.

To compensate traders for a profitable trade when they exit their position, the market contract mints the amount of OVL associated with the realized profits to the circulating supply. The market contract then returns to the trader the initial OVL collateral locked plus the newly minted OVL.

Conversely, for an unprofitable trade, the market contract removes the amount of OVL associated with the realized losses from the circulating supply, by burning upon exit a portion of the initial OVL collateral locked. The market contract then returns to the trader an amount of OVL equal to the initial collateral locked minus the burnt losses.

In this way, the passive OVL holder effectively acts as the counterparty to all unbalanced trades on Overlay markets through risk of dilution. This includes, in particular, spot OVL-ETH liquidity providers (LPs) that backstop liquidity for traders to enter and exit the system.

A simple example, without leverage and [funding payments](note-1), to illustrate.

At time \\( 0 \\),

- Total circulating supply of OVL: 8,000,000 OVL. We have: 10 OVL

- We lock 10 OVL in a long position on the \\( X \\) feed for a market entry price of \\( x=100 \\)

At a future time \\( t \\),

- The \\( X \\) feed has gone up 20%. We take profits, unwinding our position at a market exit price of \\( x=120 \\)

- The market contract mints an additional 2 OVL to the total circulating supply. It returns 12 OVL to us

- Total circulating supply of OVL: 8,000,002 OVL. We have: 12 OVL.

If the \\( X \\) feed had gone down 20% instead, the market contract would have burned 2 OVL from the circulating supply and returned 8 OVL to us. The end state would have been a total circulating supply of 7,999,998 OVL, and we would have had a balance of 8 OVL.

Things get more complex when we include leverage and funding into a peer-to-pool model, with multiple positions and traders to account for in a gas-efficient way. The purpose of this note is to outline the accounting with these dynamics at play.


## Dynamics with Leverage and Funding

### Approach

When approaching a peer-to-pool model *with leverage and funding*, we must consider what the best way would be to track both a user's share of the locked OVL in the market contract as well as their total position size -- what we're calling a user's "open interest". We define the open interest attributed to a user when building a new position on the long \\( l \\) (short \\( s \\)) side to be the number \\( N \\) of OVL locked times the leverage \\( L \\). For a position \\( j \\) on side \\( a \in \\{ l, s \\} \\), let the open interest attributed at build time \\( 0 \\) be

\\[ \mathrm{OI}\_{ja} (0) = L_{ja} \cdot N_{ja}(0) \\]

where \\( L_{ja} \\) is the leverage and \\( N_{ja}(0) \\) is the OVL collateral locked when \\( j \\) is first built.

Without funding payments, a peer-to-pool model would be relatively simple to implement. The market contract would issue shares linked to a user's portion of the collateral locked and track the initial leverage set for their position to determine PnL values. No need to worry about theirs and others' position sizes changing over time. With funding payments, however, the situation becomes more complex because collateral *and* open interest act like pooled quantities. Aggregate open interest on a side, and thus a user's share of that open interest, changes over time.

### Share of Open Interest

Funding payments are needed to balance the long vs short open interest on a market. In prior notes, we assumed the market contract could be called to execute simple periodic transfers, moving a portion of the total open interest on the long (short) side to the total open interest on the short (long) side. These funding payments draw down [risk to the system](note-4), eventually leading to a rebalancing of position sizes on a market given a long enough time horizon. The form taken for the funding payment at time \\( t \\) is

\\[ \mathrm{FP} (t) = k \cdot \mathrm{OI}\_{imb}(t) \\]

where \\( {\mathrm{OI}\_{imb}} (t) = {\mathrm{OI}_l} (t) - {\mathrm{OI}_s} (t) \\) is the open interest imbalance between the long \\( l \\) and short \\( s \\) side on a market, and \\( k \in [0, \frac{1}{2}] \\) is a per-market parameter adjustable by governance. Total open interest on side \\( a \\) is simply the sum of the open interest attributed to each position on that side

\\[ \mathrm{OI}\_{a} = \sum_{j} \mathrm{OI}\_{aj} \\]

How should this sequential transfer of *aggregate* open interest affect an individual user's share of the total collateral in the pool *and* their share of the open interest on their position's respective side?

Usually with funding payments, one would have longs (shorts) pay shorts (longs) directly from their locked collateral amounts, with their share of funding paid ideally proportional to the amount of open interest their position contributes. However, this immediately causes issues when attempting to update open interest for the imbalance calculation, since the contract must loop through all allowed leverages and their shares of the total collateral pool for both sides, which is far from ideal. Further, analyzing systemic risk becomes far more complicated vs [Note 4](note-4).

Assume a position's share of the total open interest on a side stays constant through funding. Instead of taking from (adding to) each position's collateral, the market contract shifts the open interest attributed to each position. The time evolution of the aggregate open interest on a side from time \\( t \\) (before funding) to \\( t + 1 \\) (after funding) would be

\\[ \mathrm{OI}\_l (t+1) = \mathrm{OI}\_l (t) - \mathrm{FP}(t) \\]

\\[ \mathrm{OI}\_s (t+1) = \mathrm{OI}\_s (t) + \mathrm{FP}(t) \\]

The amount a position pays (receives) each funding payment is then directly proportional to its pro-rata share of the open interest on a side

\\[ \mathrm{OI}\_{aj} (t+1) = \mathrm{OI}\_{aj} (t) \; (\mp)\_a \; \mathrm{PS}\_{aj} \cdot \mathrm{FP}(t) \\]

where we define \\( \mathrm{PS}\_{aj} \equiv \frac{\mathrm{OI}\_{aj} (t)}{\mathrm{OI}\_{a} (t)} \\) to be position \\( j \\)'s share of the total open interest on side \\( a \\). \\( (\mp)\_a = -1 \\) for \\( a  = l \\) and \\( (\mp)\_a = 1 \\) for \\( a = s \\). After \\( m \\) funding payments, the aggregate open interest imbalance reduces to

\\[ \mathrm{OI}\_{imb} (t+m) = \mathrm{OI}\_{imb} (t) \cdot ( 1 - 2k )^{m} \\]

with open interest evening out given enough time.

Funding becomes simple to implement. Assume we pay funding in discrete intervals (e.g. every [``periodSize``](note-2) blocks). A call to distribute funding payments at time \\( t+m \\), \\( m \\) intervals after the last update, should adjust a market's open interest totals according to

\\[ \mathrm{OI}\_{l} (t+m) = \frac{1}{2} \bigg[ \mathrm{OI}\_{l} (t) + \mathrm{OI}\_{s} (t) - (\mathrm{OI}\_{l} (t) - \mathrm{OI}\_{s} (t)) \cdot ( 1 - 2k )^{m} \bigg] \\]

\\[ \mathrm{OI}\_{s} (t+m) = \frac{1}{2} \bigg[ \mathrm{OI}\_{l} (t) + \mathrm{OI}\_{s} (t) + (\mathrm{OI}\_{l} (t) - \mathrm{OI}\_{s} (t)) \cdot ( 1 - 2k )^{m} \bigg] \\]

where \\( \\{\mathrm{OI}\_{l} (t), \mathrm{OI}\_{s} (t) \\} \\) are the values stored before the update.


### Accounting for Collateral
