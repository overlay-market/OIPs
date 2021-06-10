---
note: 1
oip-num: 1
title: Funding Payments
status: WIP
author: Michael Feldman (@mikeyrf), Adam Kay (@mcillkay), James Foley (@realisation)
discussions-to: oip-1
created: 2021-02-25
updated: N/A
---

Issue to address with this note:

- How do we provide opportunities for traders to earn rewards by balancing the outstanding longs vs shorts on a market?


## Stability with Fixed Pricing

Our biggest problem with Overlay is ensuring the supply of the settlement currency (OVL) remains relatively stable over longer periods of time. The goal is to limit excessive inflation that would significantly dilute all passive OVL holders who effectively act as the counterparty to all unbalanced trades, including spot OVL-ETH LPs that backstop liquidity in the system. Ideally, traders should be rewarded for stabilizing the system by taking the other side of any unbalanced market. If we can arrange this, we likely have the appropriate incentivizes for longer time horizons.

As well, keep in mind that different traders will have different preferences. For the example of an ETH-OVL feed (inverse market), some will look to make yield on their ETH, while others will look to make yield on their OVL.

For each feed, there should be at least two sets of traders with different preferences that can construct a portfolio of positions on Overlay in addition to tokens held from spot exchange swaps such that the trader in question will make yield on their chosen currency of preference by progressively stabilizing the system toward an equilibrium point.

## Problems with Floating Price

Floating the price has been ok, but introduced a large amount of additional complexity. Below, we want to explore whether we can offer opportunities for traders to construct "portfolios" that offer consistent yield while using a **fixed price** fetched directly from the oracle i.e., lock price of a new position built at a time \\( t \\) would be the price at the next oracle fetch \\( t^\* \\), where \\( t^\*\_0 < t \leq t^\* \\). Here the star denotes an oracle fetch.

We'll go into the mechanisms for accomplishing filling at price \\( P(t^\*) = P^\* \\) even though \\( P(t_0) = P_0 \\) is all of the information we have at time \\( t \\) in a separate note. The strategy in short would be: if the oracle is fetched at \\(t = t^\*\\), then the first trader in `n+1`th update interval of the feed settles all of the trades for the prior `n`th update interval (i.e. sets the price \\(P^\*\\) ), so all trades from \\( t^\*\_0 < t \leq t^\* \\) settle at the same price).

There's a good argument to be made for the benefits of fixing the price to the oracle fetch. It reduces the number of problems we have to solve from two to one. With a price fixed directly to each oracle fetch, we only have to worry about the stability of the currency supply, since arbitrage opportunities from price tracking the reference feed may not actually solve our stability problems, while also introducing other problems such as e.g., what should the price impact per OVL be.

## Imbalance and Currency Supply

Assume the same fixed price locked in by all positions entered into between \\( t^\*\_0 < t \leq t^\* \\), and assume only one market. For argument's sake, take that Overlay market to be the Uni/SushiSwap TWAP for the price of ETH in OVL terms: ETH-OVL (units of OVL/ETH).


#### Summary

We will only treat the ETH-OVL market, as it keeps things simpler. The same ideas will generalize to, say, the SUSHI-ETH market, *mutatis mutandis*.

Furthermore, we will think in terms of "internal time" to keep things simple. That is, each new block is a new time step. Thus time is discrete and we have \\(t_0, t_0+1, \ldots t-1, t, t+1, \ldots \\).

Let the open interest contributed by any one position to the long (short) side be the number \\(N \\) of OVL locked to that side, times the leverage \\(L\\) associated with those \\(N\\)  OVL. Thus, for trader \\( j \\) going long (thus the subscript \\(l\\)) we have

\\[ \mathrm{OI}\_{jl} = L_{jl} \cdot N_{jl}\\]

If that trader has multiple long positions we sum over the OI of each one:

\\[\mathrm{OI}\_{jl} = \sum_i L_{jli} N_{jli}\\]

We define the open interest on an entire market as above, summing over first \\(i\\) then \\(j\\). The imbalance on open interest is the long side OI minus the short side:
\\[\mathrm{OI}\_{imb} = \mathrm{OI}\_l - \mathrm{OI}\_s  \\]

#### The Setup

Say everyone is an OVL bull to begin with, such that they all go short the ETH-OVL feed (remember, inverse market).  We want some way to encourage traders to take the bear side of the trade, while ensuring that they are rewarded in ETH terms. Then, they are making yield on their ETH and they don't care that they are long ETH-OVL. If everyone is an OVL bear, we want the same mechanism to work for those who want to make yield in OVL terms.

This type of mechanism has already been designed before through funding payments, used as a way to incentivize having the futures price track the spot price. We should flip this on its head and instead *fix the price* but use the funding payment as a means to incentivize *balancing of position notionals* (Synthetix is also [exploring this](https://sips.synthetix.io/sips/sip-80#skew-funding-rate)).

Enforcing a funding payment from shorts to longs would work like so: we notice at \\( t_0\\) that there is an imbalance on the short side of the ETH-OVL market. At \\(t_0 + 1\\) (the next block) we take out a 1x long position on the ETH-OVL Overlay market, locking in the ETH value of our OVL collateral, and use the OVL to go long against the imbalance. Then at each \\( t = t_0 + 2, t_0 + 3,\ldots \\) we get paid a funding amount from the shorts since they are worsening the imbalance in the system while we are helping to balance the book.

What should the functional form of those funding payments \\( \mathrm{FP}(t) \\) at each time \\( t \\) be? Likely something proportional to the open interest imbalance

\\[ \mathrm{FP}(t) = k(t) \cdot \mathrm{OI}\_{imb}(t) \\]

where we use \\( k \\) as a placeholder for a "constant" adjustable by governance. This constant should be set and adjusted based on the [risk to the system](note-4) the underlying feed adds.

The *funding rate*\\( f(t) \\) imposed on each trader is the cost of holding that position, expressed in units of that trader's open interest. In other words, the funding rate is a source of return on each trader's position size. For the side \\( a \in \\{l, s\\}\\), the funding rate is defined to be

\\[ {f_a}(t) = \frac{\mathrm{FP}(t)}{\mathrm{OI}\_a(t)}. \\]

For this case 1 scenario, ETH-OVL shorts would post a negative return of \\(f_s(t) \\) and longs would post a positive return of \\( f_l(t)\\).  Conversely for case 2, where \\( \mathrm{OI}\_l > \mathrm{OI}\_s \\), the rates are defined identically but the longs pay the shorts.

For example, in the case that  \\( \mathrm{OI}\_s = 500\\) and  \\( \mathrm{OI}\_l = 200\\), we would have \\({f_s}(t) = 3k/5 \\) and \\({f_l}(t) = 3k/2 \\). Setting \\(k=1/2\\) for simplicity (this is an extreme value for \\(k\\), in practice the amount will be much lower), the shorts have a new open interest given by  

\\[ \mathrm{OI}\_s(t+1) = \mathrm{OI}\_s(t) - \mathrm{FP}(t) = \mathrm{OI}\_s(t) - f_s(t) \mathrm{OI}\_s(t) =  500 - 1500/10 = 350 \\]  

and the longs have a new open interest given by

\\[ \mathrm{OI}\_l(t+1) =\mathrm{OI}\_l(t) + \mathrm{FP}(t) = \mathrm{OI}\_l(t) + f_l(t) \mathrm{OI}\_l(t) =  200 + 600/4 = 350. \\]

Then in the case that the situation is reversed, the funding rate is reversed and the longs pay the shorts. This has eliminated the imbalance in a single time step.

These payments from the larger to the smaller open interest ultimately incentivize arbitrageurs with desire to earn yield to take offsetting positions to lock in the payment. These arbitrageurs will compete for these payments, likely incentivizing the balancing of our books until funding trends toward zero.


### Case 1: OI Long < OI Short

When \\( \mathrm{OI}\_{imb} < 0 \\), traders who want to earn yield on their ETH can 1x long ETH-OVL on Overlay, lock in the ETH value of their staked OVL ("synthetic ETH"), and get paid to take the long side of the ETH-OVL market through continuous funding. Thus, traders who prefer to denominate **in ETH terms** and wish to increase their ETH balance will compete for these funding payments until \\( \mathrm{OI}\_{imb} \to 0 \\).

#### Portfolio A: High-Yield "Synthetic ETH"

Assume as traders, we want to make yield on our ETH. We can take the traditional funding trade as an example, and execute a similar trade on the Overlay ETH-OVL market.

We buy OVL with our ETH on the spot market. Take out a 1x long position on the Overlay ETH-OVL market to lock in the notional value of our staked OVL in ETH terms. Then, this long position gets paid the funding amount above as PnL. And we will rack up funding payments until we exit, or when enough other traders take the long side so funding dries up.

For argument's sake we ignore fees for now. Because we prefer ETH, we care about our cost, value, and PnL in ETH terms. The cost in ETH terms to enter the 1x long ETH-OVL trade on Overlay is simply the cost to buy \\( n \\) OVL on the spot market, at time \\(t_0\\).

\\[ C = V_0 = \frac{n}{P_0} \\]

where \\( P_0 \\) is the price of ETH in OVL terms (units of OVL/ETH) when we enter the position. At time \\( t \\), the current value in ETH terms of our 1x long Overlay contract is

\\[ V(t) = \frac{N(t)}{P(t)} \cdot \bigg[ 1 + \frac{P(t) - P_0}{P_0} \bigg] = \frac{N(t)}{P_0} \\]

where \\( N(t) \\) is the size of our position. Note that the ETH value is locked in, and so is independent of \\(P(t)\\). Any changes in value must come from changing \\(N(t)\\).

The funding payment will probably be computed each oracle fetch rather than each block, as oracle times may vary by market and are a natural 'heartbeat'.  Consequently, let us assume there are \\(m \\) funding payments accrued between \\(t_0\\) and \\(t\\), and that each one takes place at some time \\(t_i\\) for \\(i = 1,2,\ldots,m\\). Additionally assume, for this note, that all positions are taken without leverage (that is,  \\(  L_{jli} = 1 \\)), such that a user's share of each funding payment is taken from or accrues to their OVL collateral staked. For our long position, the time evolution of our position size when factoring in funding payments is

\\[ N(t) = n \cdot \bigg( 1 + \frac{\mathrm{FP}(0)}{\mathrm{OI}\_l(0)} \bigg) \cdots \bigg( 1 + \frac{\mathrm{FP}(m-1)}{\mathrm{OI}\_l(m-1)} \bigg) = n \cdot \prod_{i=1}^m \bigg[ 1 + f_l(i) \bigg] \\]

Thus, the profit/loss **in ETH terms** at time \\(t \\) will be given by \\(\mathrm{PnL} = V(t) - C\\), yielding a PnL that changes only upon funding payments. After the $$m$$th payment, it is:

\\[ \mathrm{PnL}(m) = \frac{n}{P_0} \cdot \bigg[ \prod_{i=1}^m \bigg( 1 + f_l(i) \bigg) - 1  \bigg].\\]

This is simply getting paid funding on top of our initial ETH balance of \\( n/P_0 \\) to go long the ETH-OVL feed (bearish OVL, bullish ETH). This is always profitable for the trader that prefers ETH, when imbalance is toward the OVL bull side: shorts outweigh longs on ETH-OVL. Rate of return \\( r_{l} \\) for this strategy on the initial ETH capital \\( V_0 \\) is

\\[ r_l (m) = \prod_{i=1}^m \bigg( 1 + f_l(i) \bigg) - 1. \\]


### Case 2: OI Long > OI Short

#### Summary

When \\( \mathrm{OI}\_{imb} = \mathrm{OI}\_l - \mathrm{OI}\_s > 0 \\), traders who want to earn yield on their OVL can 1x short ETH-OVL on Overlay with half of their OVL position while selling the other half into ETH. Their aggregate "portfolio" will grow in OVL terms through continuous funding payments ("synthetic OVL"). Thus, traders who prefer to denominate **in OVL terms** and wish to increase their OVL balance will compete for these funding payments until \\( \mathrm{OI}\_{imb} \to 0 \\).

#### The Setup

Assume now that \\( \mathrm{OI}\_{imb} = \mathrm{OI}\_l - \mathrm{OI}\_s > 0 \\), so longs outweigh shorts. Traders who prefer to make yield on their OVL will compete to lock in funding payments.

#### Portfolio B: High-Yield "Synthetic OVL"

Again we make a relatively simple trade to lock in funding. If we have \\( n \\) OVL to start, we take out a 1x short position on the Overlay ETH-OVL market with \\( n / 2 \\) staked and swap \\( n / 2 \\) for ETH on the spot market. Because this trader prefers OVL, we care about our cost, value, and PnL in OVL terms.

Cost to enter the trade **in OVL terms** is just the number of OVL:

\\[ C = V_0 = n \\]

Payoff for the 1x short is

\\[ \mathrm{PO}(t) = \frac{N(t)}{2} \cdot \bigg[ 1 - \frac{P(t) - P_0}{P_0} \bigg] \\]

and value of the spot ETH in OVL terms at time \\( t\\) is \\( (n / 2) \cdot (P(t) / P_0) \\). Value of the portfolio at \\( t \\) is then

\\[ V(t) = \frac{n}{2} \cdot \frac{P(t)}{P_0} + \frac{N(t)}{2} \cdot \bigg[1 - \bigg( \frac{P(t)}{P_0} - 1 \bigg) \bigg] \\]

Similar to the prior case, assume for this note that funding only affects the user's collateral (disregard leverage considerations), such that

\\[ N(t) = n \cdot \prod_{i=1}^m \bigg( 1 + f_s (i) \bigg) \\]

Going through the same exercise as in the previous case with \\( P(t) = P_0 \cdot (1 + \epsilon) \\) gives a PnL of

\\[ \mathrm{PnL}(t) = \frac{n}{2} \cdot (1 - \epsilon) \cdot \bigg[ \prod_{i=1}^m \bigg( 1 + f_s (i) \bigg) - 1 \bigg] \\]

which is simply getting paid funding on top of our initial OVL balance of to go short the ETH-OVL feed (bullish OVL, bearish ETH). This is profitable for the trader that prefers OVL, when \\( \epsilon < 1 \\) and imbalance is toward the OVL bear side: longs outweigh shorts on ETH-OVL. Rate of return \\( r_{s} \\) for this strategy on the initial OVL capital \\( V_0 \\) is

\\[ r_s (t) = \frac{1 - \epsilon}{2} \cdot \prod_{i=1}^m \bigg[ \bigg( 1 + f_s(i) \bigg) - 1 \bigg] \\]

which is still sensitive to changes in the ETH-OVL feed, but remains profitable as long as price deviations are less than 100% to the ETH bull side.

## Magic ERC-20s

What's even more interesting is these are simple trades that anyone should be able to participate in. Since portfolio A mimics holding spot ETH tokens and portfolio B mimics holding spot OVL, each with additional yield from funding payments, we can represent these portfolios as high-yield synthetic fungible tokens. What we're calling Magic ETH (portfolio A) and Magic OVL (portfolio B).

Users would deposit ETH to the Magic ETH contract and OVL to the Magic OVL contract. Each magic contract would then perform the appropriate swaps and building of Overlay market positions necessary to replicate the portfolios above and issue [ERC-20](https://eips.ethereum.org/EIPS/eip-20) tokens as corresponding credits.  These are effectively tokenized basis trades that users can easily swap into or out of on spot AMMs as funding rates go against their respective side or provide liquidity for on spot exchanges specializing in like-asset pairs (e.g. Magic ETH & ETH pool).

Each Overlay market we offer that includes OVL as one of the currencies will have a similar dynamic. Another way to generate Magic OVL (portfolio B), and a new Magic X high-yield synthetic for the X-OVL market (portfolio A). Likely, our first markets would be ETH-OVL and DAI-OVL for Magic ETH, DAI, and OVL at launch. The additional liquidity generated from providing easy-to-access exposure to funding on Overlay markets could ultimately stabilize our system even more through larger amounts of capital interested in playing the basis trade.

### Strategies

We can code and propose strategies for [yearn vaults](https://github.com/iearn-finance/yearn-vaults) that swap in and out of each magic token to avoid losing principal: one to earn yield on OVL and the other to earn yield on ETH, although gas costs could likely be difficult to manage. The alternative would be to open source Python bots that anyone can run on their own servers, like [Hummingbot](https://hummingbot.io/) strategies.

# Considerations

## Setting \\( k \\)

We will explore the required value of \\( k \\) in more depth in [risk to the system](note-4). However, for now we note that (assuming no trades are made) the next value of the imbalance, calculated after funding, satisfies the recurrence relation  \\( \mathrm{OI}\_{imb}(m+1) = \mathrm{OI}\_{imb}(m)(1 -2k)\\). This may easily be solved, yielding for the $$m$$th funding payment (where 0 means no funding has been made):

\\[ \mathrm{OI}\_{imb}(m) = \mathrm{OI}\_{imb}(0)\cdot \bigg(1 -2k\bigg)^m  \\]

If we define \\( 0 < \ell < 1 \\) such that

\\[ \mathrm{OI}\_{imb}(m) = \ell \cdot \mathrm{OI}\_{imb}(0)\\]

then we can explictly solve for \\(k \\) as a function of \\( \ell, m\\). Below, we give a table where the leftmost column is \\( \ell \\), and values of \\( m \\) are from 1 through 9. Intuitively, it tells us what value of \\( k \\) we need to pick in order to have \\( \ell \\) imbalance left after \\( m \\) funding payments.

| \\(\ell \\) | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| --- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| 0.1 | 0.450 | 0.342 | 0.268 | 0.219 | 0.185 | 0.159 | 0.140 | 0.125 | 0.113 |
| 0.2 | 0.400 | 0.276 | 0.208 | 0.166 | 0.138 | 0.118 | 0.103 | 0.091 | 0.082 |
| 0.3 | 0.350 | 0.226 | 0.165 | 0.130 | 0.107 | 0.091 | 0.079 | 0.070 | 0.063 |
| 0.4 | 0.300 | 0.184 | 0.132 | 0.102 | 0.084 | 0.071 | 0.061 | 0.054 | 0.048 |
| 0.5 | 0.250 | 0.146 | 0.103 | 0.080 | 0.065 | 0.055 | 0.047 | 0.041 | 0.037 |
| 0.6 | 0.200 | 0.113 | 0.078 | 0.060 | 0.049 | 0.041 | 0.035 | 0.031 | 0.028 |
| 0.7 | 0.150 | 0.082 | 0.056 | 0.043 | 0.034 | 0.029 | 0.025 | 0.022 | 0.019 |
| 0.8 | 0.100 | 0.053 | 0.036 | 0.027 | 0.022 | 0.018 | 0.016 | 0.014 | 0.012 |

## Remaining Risk

The risk of a OVL price death spiral still exists when incorporating funding payments, even with a profitable portfolio for case 2. If there is complete loss of faith in OVL and the price collapses while longs heavily outweigh shorts on the ETH-OVL feed, there may be few traders willing to earn yield in OVL and thus take the short side of the trade, even though funding payments would be extremely profitable in OVL terms. Longs on ETH-OVL could ultimately still win in the short term, mint more OVL, then cash out that OVL, suppressing the value of OVL relative to ETH more and having even more longs on ETH-OVL win. It is a positive feedback loop that is difficult to mitigate without enforcing strict values for \\( k \\) and imposing caps. Even then, this scenario is still very much a risk for the Overlay system.
