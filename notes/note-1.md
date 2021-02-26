---
note: 1
oip-num: 1
title: Funding Payments
status: WIP
author: Michael Feldman (@mikeyrf)
discussions-to: oip-1
created: 2021-02-25
updated: N/A
---

## Stability with Fixed Pricing

Our biggest outstanding problem with Overlay is ensuring the currency supply remains stable over time. Ideally, traders should make money from stabilizing the system. If we can arrange this, we have the appropriate incentivizes to be confident this will work over longer periods of time.

We must also keep in mind that different traders will have different preferences. Some will look to make yield on their ETH, while others will look to make yield on their OVL (for the example of an OVL-ETH feed).

For each feed, there should be at least two sets of traders with different preferences that can construct a portfolio of positions on Overlay in addition to tokens held from spot exchange swaps such that the trader in question will make yield on their chosen currency of preference by progressively stabilizing the system toward an equilibrium point.

## Problems with Floating Price

Floating the price has been ok, but introduced a large amount of additional complexity. Below, I want to explore whether we can offer opportunities for traders to construct "portfolios" that offer consistent yield while using a **fixed price** fetched directly from the oracle i.e., lock price of a new position built at a time \\( t \\) would be the price at the next oracle fetch \\( t_1 \\), where \\( t_0 < t < t_1 \\).

I'll go into the mechanisms for accomplishing filling at \\( P_1 \\) even though \\( P_0 \\) is all of the information we have at time \\( t \\) in a separate README. The strategy in short would be: the `n+1`th trader settles the trades for the prior `n`th trader (readjusts price to value at \\( t_1 \\)).

Daniel (@dwasse) made a good argument for the benefits of fixing the price to the oracle fetch. It reduces then number of problems we have to solve from two to one. With a price fixed directly to each oracle fetch, we only have to worry about the stability of the currency supply, since arbitrage opportunities from price tracking the reference feed may not actually solve our stability problems, while also introducing other problems such as e.g., what should the price impact per OVL be.

## Imbalance and Currency Supply

Assume the same fixed price locked in by all positions entered into between \\( t_0 < t < t_1 \\), and assume only one market. For argument's sake, take that Overlay market to be the SushiSwap TWAP for the price of OVL in ETH terms: OVL-ETH.

### Case 1: OI Long > OI Short

#### Summary

When the time-weighted average of the open interest on the long side is greater than the short side \\( \mathrm{TWAOI}\_{imb} = \mathrm{TWAOI}_l - \mathrm{TWAOI}_s > 0 \\), traders who want to earn yield on their ETH can 1x short OVL-ETH on Overlay, lock in the ETH value of their staked OVL to first order in price changes, and get paid to take the short side of the OVL-ETH market through continuous funding. Thus, traders who prefer to denominate **in ETH terms** and wish to increase their ETH balance will complete for these funding payments until \\( \mathrm{TWAOI}\_{imb} \xrightarrow[]{} 0 \\).

#### The Setup

Say everyone goes long to begin with. We'll denote the time-weighted average of the notional imbalance on a market between longs and shorts as \\( \mathrm{TWAOI}\_{imb} = \mathrm{TWAOI}_l - \mathrm{TWAOI}_s \\), where I'm using \\( \mathrm{OI} \\) for open interest and \\( \mathrm{TWAOI}\_{imb} > 0 \\) in this scenario.

Now, what we want is some way to encourage traders to take the short side of the trade, while ensuring that they make money in ETH terms. Then, they are making yield on their ETH and they don't care that they are short OVL-ETH.

This type of mechanism has already been designed before through funding payments, used as a way to incentivize having the futures price track the spot price. We should flip this on its head and instead *fix the price* but use the funding payment as a means to incentivize *balancing of position notionals* (Synthetix is also [exploring this](https://sips.synthetix.io/sips/sip-80#skew-funding-rate) for their futures product).

Enforcing a funding payment from longs to shorts at the next oracle fetch \\( t_1 \\) would work like so: I take out a 1x short position on the OVL-ETH Overlay market, locking in the ETH value of my OVL collateral staked to first order in price changes given we use linear contracts. Then at \\( t_1 \\), I get paid a funding amount from the longs since they are worsening the imbalance in the system while I am helping to balance the book.

What should the functional form of that funding rate be? Something proportional to the time-weighted average of the open interest imbalance

\\[ f_i = k(t_{i-1}, t_i) \cdot \frac{\mathrm{TWAOI}\_{imb}(t_i)}{\mathrm{TWAOI}\_{l}(t_i) + \mathrm{TWAOI}\_{s}(t_i)} \\]

where we use \\( k \\) as a placeholder for a spring-like "constant" adjustable by governance, likely related to the vol of the underlying feed. Depending on the form of \\( k \\), Overlay still takes on some directional risk but these payments from longs to shorts when \\( \mathrm{TWAOI}\_{imb} > 0 \\) ultimately incentivize traders to take out short positions to lock in this payment at \\( t_1 \\). Traders with similar preferences (i.e. desire to earn yield on ETH) will compete for these payments with more rushing to the short side over time, likely incentivizing the balancing of our books until funding trends toward zero.


#### Portfolio Construction

Assume as a trader, I want to make yield on my ETH. I can take [this trade]((https://coinhax.com/guides/BitMEX-Funding/bitmex-btc-short-funding.html)) as an example, and execute a similar trade on the Overlay OVL-ETH market.

I buy OVL with my ETH on the spot market. Take out a 1x short position on the Overlay OVL-ETH market to lock in the notional value of my staked OVL in ETH terms (this is almost completely hedged but, as shown below, still has some OVL price exposure). Then, this short position gets paid the funding amount above. And I will rack up funding payments until I exit at some time in the future \\( t_n \\) or when enough other traders take the short side so funding dries up.

For argument's sake, take \\( t = t_0 \\) and ignore fees for now. Because this trader prefers ETH, I care about my cost, value, and PnL in ETH terms. The cost in ETH terms to enter the short 1x OVL-ETH trade on Overlay is simply the cost to buy OVL on the spot market.

\\[ C = P_0 \cdot n_{OVL} \\]

where \\( n_{OVL} \\) is the number of OVL I swapped for on the spot market and \\( P_0 \\) is the price of OVL in ETH terms. The payoff of my 1x short Overlay contract is

\\[ \mathrm{PO}(t_n) = n_{OVL} \cdot [ 1 - (P_n - P_0) / P_0 ] \\]

and so the total value of my 1x short "portfolio" at \\( t_n \\) in ETH terms is

\\[ V(t_n) = P_n \cdot n_{OVL} \cdot [ 1 - (P_n - P_0) / P_0 + \sum_{i=0}^{n} f_i ] \\]

where for \\( f_i \\) substitute in the expression above for our funding payments. Thus, my \\( \mathrm{PnL}(t_n) = V(t_n) - C \\) for this 1x short trade **in ETH terms** is

\\[ \mathrm{PnL}(t_n) = P_n \cdot n_{OVL} \cdot [ 2 - ( P_n / P_0 + P_0 / P_n ) + \sum_{i=0}^{n} f_i ] \\]

Let \\( P_n = P_0 \cdot (1 + \epsilon_n) \\), and assume \\( \|\epsilon_n\| < 1 \\) for our purposes. Then,

\\[ \mathrm{PnL}(t_n) = P_n \cdot n_{OVL} \cdot [ 2 - ( 1 + \epsilon_n + 1 / (1 + \epsilon_n) ) + \sum_{i=0}^{n} f_i ] \\]

Taylor expanding \\( 1/(1 + \epsilon_n) = 1 - \epsilon_n + \epsilon_n^2 - \epsilon_n^3 + ... \\), my PnL in ETH terms for the 1x short to balance the system is

\\[ \mathrm{PnL}(t_n) = P_n \cdot n_{OVL} \cdot [ \sum_{i=0}^{n} f_i - \epsilon_n^2 + \epsilon_n^3 + ... ] \\]

which is simply getting paid funding to go short to first order in \\( \epsilon_n \\). The higher order \\( \epsilon_n \\) terms are the reason we are not completely hedged from OVL price exposure in this trade. We could use an inverse contract payoff instead of the linear payoff we've adopted to eliminate these higher order terms, but there are issues with minting an infinite number of tokens if OVL-ETH price heads toward zero that we don't want. I'd suggest keeping the linear payoff for simplicity.


### Case 2: OI Long < OI Short

#### Summary

When \\( \mathrm{TWAOI}_{imb} = \mathrm{TWAOI}_l - \mathrm{TWAOI}_s < 0 \\), traders who want to earn yield on their OVL can 1x long OVL-ETH on Overlay with half of their OVL position while selling the other half into ETH. Their aggregate "portfolio" will grow in OVL terms through continuous funding payments to second order in price changes. Thus, traders who prefer to denominate **in OVL terms** and wish to increase their OVL balance will complete for these funding payments until \\( \mathrm{TWAOI}\_{imb} \xrightarrow[]{} 0 \\).

#### The Setup

Assume now that \\( \mathrm{TWAOI}\_{imb} = \mathrm{TWAOI}_l - \mathrm{TWAOI}_s < 0 \\), so shorts outweigh longs. Traders who prefer to make yield on their OVL will compete to lock in funding payments.


#### Portfolio Construction

Relatively simple trade to lock in funding. If I have \\( n_{OVL} \\) to start, I take out a 1x long position on the Overlay OVL-ETH market with \\( n_{OVL} / 2 \\) staked and swap \\( n_{OVL} / 2 \\) for ETH on the spot market. Because this trader prefers OVL, I care about my cost, value, and PnL in OVL terms.

Cost to enter the trade **in OVL terms** is

\\[ C = n_{OVL} \\]

Payoff for the 1x long is

\\[ \mathrm{PO}(t_n) = (n_{OVL} / 2) \cdot [ 1 + (P_n - P_0) / P_0 ] \\]

and value of the spot ETH in OVL terms at time \\( t_n \\) is \\( (n_{OVL} / 2) \cdot (P_0 / P_n) \\). Value of the portfolio at \\( t_n \\) is then

\\[ V(t_n) = (n_{OVL} / 2) \cdot [(P_0 / P_n) + 1 + (P_n - P_0) / P_0 + \sum_{i=0}^{n} f_i ] \\]

Going through the same exercise as in the previous case and Taylor expanding for \\( P_n = P_0 \cdot (1 + \epsilon_n) \\) gives my PnL of

\\[ \mathrm{PnL}(t_n) = ( n_{OVL} / 2 ) \cdot [ \sum_{i=0}^{n} f_i + \epsilon_n^2 - \epsilon_n^3 + ... ] \\]

which is profitable to second order in \\( \epsilon_n \\).


## Public Strategies

What's even more interesting is these are simple trades that anyone should be able to participate in. We can code and propose strategies for [yearn vaults](https://github.com/iearn-finance/yearn-vaults) that accomplish this: one to earn yield on OVL and the other to earn yield on ETH. This ultimately stabilizes our system even more given TVL for yearn is on the order of [$500M - $1B](https://defipulse.com/yearn.finance) as of Feb 2021.

The alternative would be to open source Python bots that anyone can run on their own servers, although gas costs here would be difficult. The benefit of proposing strategies for yearn would be community access to yield and the gas savings from aggregation of funds.
