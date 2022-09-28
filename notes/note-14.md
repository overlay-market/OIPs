---
note: 8
oip-num: 1
title: Multi Collateral Positions 
status: WIP
author: James Foley (@realisation)
discussions-to: oip-1
created: 2021-06-12
updated: N/A
---

Issue to address with this note:

- How can we accept variable collateral for positions in OVL?

## Context

We had been discussing multicollateral positions on and off, previously lining them up as an aspect for version two of the protocol. Recently an epiphany dawned on me about an efficient way to accompish multicollateral positions, where we architect the core contracts such that there are collateral managers and markets with a many to many mapping between them. For instance, one collateral manager can interact with many markets and one market can interact with many collateral managers.

### Background

With collateral managers, we can manage positions with payout and open interest expressed in OVL terms with alternative collateral types. This can be as simple as OVL collateral, but can also support other collateral types. Other collateral types can be seen as taking on an implied leverage as the value of the collateral rises and falls in OVL terms.

In order to accept other collateral types, we need to be able to value them at any time as well as realize the OVL value of the collateral in the case of a liquidation or unwinding an unprofitable position. As long as those two requirements are fulfilled, we will be able to accept any arbitrary collateral. This could range from OVL adjacent ERC20s to non adjacent ERC20s, with adjacency defined as having a spot market paired with OVL with deep liquidty. If there was no LINK/OVL market, there is a LINK/ETH market, so there is a path OVL->ETH->LINK and LINK->ETH->OVL. This opens up collateral to potentially any ERC20, from standard assets to yield bearing strategies or to LP shares. There could also be a collateral manager for other positions on Overlay. Further, there could be collateral managers for non traditional feeds such as Upshot, so long as there were liquid on chain markets, allowing us to realize OVL in an unwinding/liquidation.

## ERC20 Collateral by way of Uniswap V3

Starting with the Uniswap collateral manager, the naive idea is that we would accept ERC20 collateral by swapping it immediately into OVL and building a position with it as collateral. This is less than ideal since the swap into OVL will incur a 30 bp fee in addition to any slippage and frontrunning exposure, chipping away at the user's principle before it is even entered into a position, at which point we exact yet another fee. 

More desirably, assuming users will take out reasonable positions that will not be liquidated, this can be avoided altogether where we can simply credit the user with OI relative to the OVL terms of the collateral posted. For instance, if the TWAP of the ETH/OVL price reads .5 and the user opened up a position with 2 ETH, then our collateral manager would escrow the user's ETH and credit them with a position worth 1 OVL of OI. The importance then becomes how to track their collateral value as the price of ETH/OVL fluctuates, perhaps it goes to .25, or up to 1.

Given the nature of our bookkeeping where we have OI as a single dynamic value which spares us the requirement of looping through each respective position in adjusting their collateral amounts, we have to now adjust the collateral amount of our positions not just according to funding paid/received but also according to the fluctuations of collateral value in OVL terms. 

### Reframing Collateral in OVL terms

Take the expression for the collateral of a position at any given time 

\\[ N\_{aj} (t) \equiv \mathrm{OI}\_{aj} (t) - D_{aj} \\]

If the price of ETH/OVL at inception of the position is .5, then goes down to .25 during the position's lifetime, then this equation no longer holds true because we record the debt as a static value and 1 ETH is no longer worth 2 OVL but only .5 OVL, therefore OI - debt will would yield 2 OVL which is 4 ETH at the current time.

In order to compensate for this, we can rewrite the above equation by including the price delta in OVL terms between now and the time the collateral was used to open the position. We can define that as 

\\[ P\_{d} (t) \equiv ( P_{exit} - P_{entry} ) / P_{entry} \\]

When plugged into our collateral value yields

\\[ N\_{aj} (t) \equiv ( \mathrm{OI}\_{aj} (t) - D_{aj} ) * (1 + P_{d}) \\]

Thus providing an accurate reading of the collateral value with respect to OVL terms while allowing the OI to fluctuate with payments to the longs and the shorts. 

### Profitable unwinds

On unwind, should the user's position be profitable in OVL terms in addition to their collateral being above the maintenance margin in OVL, then we mint the outstanding PnL in OVL and send it to the user along with their ERC20 collateral, or as a convenience swap it on spot to the ERC20 asset and send them both together. 

Outstanding question - since taking out an Overlay position with non OVL collateral entails implied leverage, how do we manage the payout? Do we mint against their current collateral amount? Or do we mint against the credited cost in OVL terms even though their collateral has grown or shrunk? It would seem the latter. 

### Unprofitable unwinds and liquidations

If a user's position is unprofitable on unwind or even so unprofitable that it becomes liquidated, then we need to take action with the collateral and use it to buy back and burn OVL. 

In these scenarios, we will be contending with slippage as well as AMM fees, so what steps do we take to ensure that the system never winds up eating position that is underwater?
