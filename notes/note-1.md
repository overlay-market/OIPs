---
note: 1
oip-num: 1
title: Funding Payments
status: WIP
author: Michael Feldman (@mikeyrf), Adam Kay (@mcillkay)
discussions-to: oip-1
created: 2021-02-25
updated: N/A
---

Issue to address with this note:

- How do we provide opportunities for traders to make money by balancing the outstanding longs vs shorts on a market?


## Stability with Fixed Pricing

Our biggest problem with Overlay is ensuring the supply of the settlement currency (OVL) remains relatively stable over longer periods of time. The goal is to limit excessive inflation that would significantly dilute all passive OVL holders who effectively act as the counterparty to all unbalanced trades, including spot OVL-ETH LPs that backstop liquidity in the system. Ideally, traders should make money from stabilizing the system by taking the other side of any unbalanced trade. If we can arrange this, we likely have the appropriate incentivizes for longer time horizons.

As well, keep in mind that different traders will have different preferences. For the example of an OVL-ETH feed, some will look to make yield on their ETH, while others will look to make yield on their OVL.

For each feed, there should be at least two sets of traders with different preferences that can construct a portfolio of positions on Overlay in addition to tokens held from spot exchange swaps such that the trader in question will make yield on their chosen currency of preference by progressively stabilizing the system toward an equilibrium point.

## Problems with Floating Price

Floating the price has been ok, but introduced a large amount of additional complexity. Below, we want to explore whether we can offer opportunities for traders to construct "portfolios" that offer consistent yield while using a **fixed price** fetched directly from the oracle i.e., lock price of a new position built at a time \\( t \\) would be the price at the next oracle fetch \\( t^\* \\), where \\( t^\*\_0 < t < t^\* \\). Here the star denotes an oracle fetch.


We'll go into the mechanisms for accomplishing filling at price \\( P(t^\*) = P^\* \\) even though \\( P(t_0) = P_0 \\) is all of the information we have at time \\( t \\) in a separate note. The strategy in short would be: if the oracle is fetched at \\(t = t_n\\), then the first trader in `n+1`th update interval of the feed settles all of the trades for the prior `n`th update interval (i.e. sets the price \\(P_n^\*\\) ), so all trades from \\( t^\*\_0 < t < t_n^\* \\) settle at the same price).

There's a good argument to be made for the benefits of fixing the price to the oracle fetch. It reduces the number of problems we have to solve from two to one. With a price fixed directly to each oracle fetch, we only have to worry about the stability of the currency supply, since arbitrage opportunities from price tracking the reference feed may not actually solve our stability problems, while also introducing other problems such as e.g., what should the price impact per OVL be.

## Imbalance and Currency Supply

Assume the same fixed price locked in by all positions entered into between \\( t^\*\_0 < t < t^\* \\), and assume only one market. For argument's sake, take that Overlay market to be the Uni/SushiSwap TWAP for the price of OVL in ETH terms: OVL-ETH.


#### Summary
We will only treat the OVL-ETH market, as it keeps things simpler. The same ideas will generalize to, say, the SUSHI-ETH market, *mutatis mutandis*.

Furthermore, we will think in terms of "internal time" to keep things simple. That is, each new block is a new time step. Thus time is discrete and we have \\(t_0, t_0+1, \ldots t-1, t, t+1, \ldots \\).

Let the open interest contributed by any one position to the long (short) side be the number \\(N \\) of OVL locked to that side, times the leverage \\(L\\) associated with those \\(N\\)  OVL. Thus, for trader \\( j \\) going long (thus the subscript \\(l\\)) we have

\\[ \mathrm{OI}\_{jl} = L_{jl} \cdot N_{jl}\\]

If that trader has multiple long positions we sum over the OI of each one:

\\[\mathrm{OI}\_{jl} = \sum_i L_{jli} N_{jli}\\]

We define the open interest on an entire market as above, summing over first \\(i\\) then \\(j\\). The imbalance on open interest is the long side OI minus the short side:
\\[\mathrm{OI}\_{imb} = \mathrm{OI}\_l - \mathrm{OI}\_s  \\]

#### The Setup

Say everyone goes long to begin with.  We want some way to encourage traders to take the short side of the trade, while ensuring that they make money in ETH terms. Then, they are making yield on their ETH and they don't care that they are short OVL-ETH. If everyone is short, we want the same mechanism to work for those who want to make yield in OVL terms.

This type of mechanism has already been designed before through funding payments, used as a way to incentivize having the futures price track the spot price. We should flip this on its head and instead *fix the price* but use the funding payment as a means to incentivize *balancing of position notionals* (Synthetix is also [exploring this](https://sips.synthetix.io/sips/sip-80#skew-funding-rate) for their futures product).

Enforcing a funding payment from longs to shorts would work like so: we notice at \\( t_0\\) that there is an imbalance on the long side. At \\(t_0 + 1\\) (the next block) we take out a 1x short position on the OVL-ETH Overlay market, locking in the ETH value of our OVL collateral, and  use the OVL to go short against the imbalance. Then at each \\( t = t_0 + 2, t_0 + 3,\ldots \\) we get paid a funding amount from the longs since they are worsening the imbalance in the system while we are helping to balance the book.

What should the functional form of those funding payments \\( \mathrm{FP}(t) \\) at each time \\( t \\) be? Likely something proportional to the open interest imbalance

\\[ \mathrm{FP}(t) = k(t) \cdot \mathrm{OI}\_{imb}(t) \\]

where we use \\( k \\) as a placeholder for a "constant" adjustable by governance. This constant should be set and adjusted based on the [risk to the system](note-4) the underlying feed adds.

The *funding rate*\\( f(t) \\) imposed on each trader is the cost of holding that position, expressed in units of that trader's open interest. In other words, the funding rate is a source of return on each trader's position. For the side \\( a \in \\{l, s\\}\\), the funding rate is defined to be

\\[ {f_a}(t) = \frac{\mathrm{FP}(t)}{\mathrm{OI}\_a(t)}. \\]

For this case 1 scenario, longs would post a negative return of \\(f_l(t) \\) and shorts would post a positive return of \\( f_s(t)\\).  Conversely for case 2, where \\( \mathrm{OI}\_l < \mathrm{OI}\_s \\), the rates are defined identically but the shorts pay the longs.

For example, in the case that  \\( \mathrm{OI}\_l = 500\\) and  \\( \mathrm{OI}\_s = 200\\), we would have \\({f_l}(t) = 3k/5 \\) and \\({f_s}(t) = 3k/2 \\). Setting \\(k=1/2\\) for simplicity (this is an extreme value for \\(k\\), in practice the amount will be much lower, see [risk to the system](note-4)), the longs have a new open interest given by  

\\[ \mathrm{OI}\_l(t+1) = \mathrm{OI}\_l(t) - \mathrm{FP}(t) = \mathrm{OI}\_l(t) - f_l(t) \mathrm{OI}\_l(t) =  500 - 1500/10 = 350 \\]  

and the shorts have a new open interest given by

\\[ \mathrm{OI}\_s(t+1) =\mathrm{OI}\_s(t) + \mathrm{FP}(t) = \mathrm{OI}\_s(t) + f_s(t) \mathrm{OI}\_s(t) =  200 + 600/4 = 350. \\]

Then in the case that the situation is reversed, the funding rate is reversed and the shorts pay the longs. This has eliminated the imbalance in a single time step.

These payments from the larger to the smaller open interest ultimately incentivize arbitrageurs with desire to earn yield to take offsetting positions to lock in the payment. These arbitrageurs will compete for these payments, likely incentivizing the balancing of our books until funding trends toward zero.


### Case 1: OI Long > OI Short

When \\( \mathrm{OI}\_{imb} > 0 \\), traders who want to earn yield on their ETH can 1x short OVL-ETH on Overlay, lock in the ETH value of their staked OVL to first order in price changes, and get paid to take the short side of the OVL-ETH market through continuous funding. Thus, traders who prefer to denominate **in ETH terms** and wish to increase their ETH balance will complete for these funding payments until \\( \mathrm{OI}\_{imb} \to 0 \\).

#### Portfolio Construction

Assume as traders, we want to make yield on our ETH. We can take the traditional short trade as an example, and execute a similar trade on the Overlay OVL-ETH market.

We buy OVL with our ETH on the spot market. Take out a 1x short position on the Overlay OVL-ETH market to lock in the notional value of our staked OVL in ETH terms (this is almost completely hedged but, as shown below, still has some OVL price exposure). Then, this short position gets paid the funding amount above. And we will rack up funding payments until we exit at some time in the future \\( t_n \\) or when enough other traders take the short side so funding dries up.

For argument's sake we ignore fees for now. Because we prefer ETH, we care about our cost, value, and PnL in ETH terms. The cost in ETH terms to enter the short 1x OVL-ETH trade on Overlay is simply the cost to buy OVL on the spot market, at time \\(t_0\\).

\\[ C = P_0 \cdot n \\]

where \\( n \\) is the number of OVL purchased on the spot market and \\( P_0 \\) is the price of OVL in ETH terms (units of ETH/OVL) when we enter the position. At time \\( t \\), the current value in ETH terms of our 1x short Overlay contract without funding considerations is

\\[ V(t) = P(t) \cdot N(t) \cdot \bigg[ 1 - \frac{P(t) - P_0}{P_0} \bigg].\\]

where \\( N(t) \\) is the amount of collateral attributed to our position from the collateral pool. The funding payment will probably be computed each oracle fetch rather than each block, as oracle times may vary by market and are a natural 'heartbeat'.  Consequently, let us assume there are \\(m \\) funding payments accrued between \\(t_0\\) and \\(t\\), and that each one takes place at some time \\(t_i\\) for \\(i = 1,2,\ldots,m\\). Additionally assume, for this note, that all positions are taken without leverage \\(  L_{jli} = 1 \\), such that a user's share of each funding payment is taken from or accrues to their OVL collateral staked. For our short position

\\[ N(t) = n \cdot \bigg( 1 + \frac{\mathrm{FP}(0)}{\mathrm{OI}\_s(0)} \bigg) \cdots \bigg( 1 + \frac{\mathrm{FP}(m-1)}{\mathrm{OI}\_s(m-1)} \bigg) = n \cdot \prod_{i=0}^{m-1} \bigg[ 1 + f_s(i) \bigg] \\]

Thus, the profit/loss **in ETH terms** at time \\(t \\) will be given by \\(\mathrm{PnL} = V - C\\), yielding:

\\[\mathrm{PnL}(t) =  P(t) \cdot n \cdot \prod_{i=0}^{m-1}\bigg( 1 + f_s(i) \bigg) \cdot \bigg[ 1 - \bigg( \frac{P(t)}{P_0} - 1 \bigg) \bigg] - P_0 \cdot n \\]

Let

\\[ P(t) = P_0 \cdot (1 + \epsilon) \\]

Then, our PnL in ETH terms for the 1x short to balance the system is

\\[ \mathrm{PnL}(t_m) = P_0 \cdot n \cdot \bigg[ (1 - \epsilon^2) \prod_{i=0}^{m-1} \bigg( 1 + f_s(i) \bigg) - 1  \bigg] \\]

which is simply getting paid funding to go short to first order in \\( \epsilon \\), as \\( f_s(i) > 0 \; \forall i \\) in this scenario.

The second order term \\( \epsilon^2 \\) is the reason we are not completely hedged from OVL price exposure in this trade. We could use an inverse contract payoff instead of the linear payoff we've adopted to eliminate these higher order terms, but there are issues with minting an infinite number of tokens if OVL-ETH price heads toward zero that we don't want (see [below](#remaining-risk)).

The condition for this funding trade to be profitable for arbitrageurs is

\\[  \prod_{i=0}^{m-1} \bigg( 1 + f_s (i) \bigg) > \frac{1}{1 - \epsilon^2} \\]

which simply says funding payment compounding needs to outpace any second order deviations in price.

It is instructive to look at the simplistic case of only one trader entering in on the short side. We seek an expression for this profitability condition for a single trader in terms of the initial imbalance.  After \\(m\\) funding payments, the open interest on the short side satisfies the relation

\\[\mathrm{OI}\_s(m) = \mathrm{OI}\_s(0) + \sum_{i=0}^{m-1} \mathrm{FP}(i) = \mathrm{OI}\_s(0) + k \mathrm{OI}\_{imb}(0) \sum_{i=0}^{m-1} (1 - 2k)^i \\]

Over longer time horizons, we can approximate with \\(m \to \infty\\) and notice that \\(\|1-2k\|<0\\), allowing us to use the closed form expression of the geometric series. Thus when \\(m\\) is large enough, the change in open interest due to funding payments in OVL terms is:

\\[\mathrm{OI}\_s(m) - \mathrm{OI}\_s(0) \approx k \mathrm{OI}\_{imb}(0)\sum_{i=0}^\infty(1-2k)^i = \frac{k \mathrm{OI}\_{imb}(0)}{1 - (1-2k)} = \frac{\mathrm{OI}\_{imb}(0)}{2} \\]

As expected then, the profit for those going short is one half the imbalance. Noting that for large enough \\( m \\)
\\[ \sum_{i=0}^{m-1} \mathrm{FP}(i) \approx \frac{\mathrm{OI}\_{imb}(0)}{2} \\]
and assuming for simplicity that there is a single  arbitrageur, we obtain the condition for this trader to be economically motivated to collect funding payments (i.e. make a profit):

\\[ \mathrm{OI}\_{imb}(0) > \frac{2n\epsilon^2}{1-\epsilon^2} \\]

Clearly, \\( n\\) can be set vanishingly small, corresponding to the fact that we have not set a minimum value required to collect payments. Thus, the funding payment mechanism becomes an auction in which all arbitrageurs try to outbid others while keeping their \\( n \\) as small as possible.

Say we imposed a minimum on the bet required to collect funding, as some fraction \\( \alpha \\) of the initial imbalance. We obtain

\\[ 1 > \frac{2\alpha\epsilon^2}{1-\epsilon^2} \\]

which gives single-trader profitably constraints on \\( \epsilon \\) in terms of \\(\alpha \\) for the 1x short funding trade of \\( \epsilon \in [- \frac{1}{\sqrt{1+2\alpha}} , \frac{1}{\sqrt{1+2\alpha}} ] \\). Extreme values for \\( \alpha \\) of .1 gives max and min values on \\( \epsilon \\) for the trade to remain profitable of .9129 and -.9129, respectively, and an \\(\alpha \\) value of .9 gives .5976 and -.5976. Remember, \\( \epsilon \\) represents the *deviation* in price \\( P(t) \\) from \\( P_0 \\), so a max value of .913 would mean the funding trade is profitable as long as the price doesn't increase more than 91.3% from \\( t_0 \\) to \\(t\\).

For a reasonable \\( \alpha \\) of .33, we have \\( \epsilon = (.7762, -.7762) \\).  We can thus conclude that the nonlinearity will not effect things and that the hedging mechanism will, in practice, be quite robust.

Finally, note that the above expression is independent of \\( k \\), because we made the long-time assumption \\( m \to \infty\\). In practice,  \\( k\\) becomes more relevant the smaller it is. We can make various estimates, replacing the factor of 2 with increasingly larger numbers as \\( k\\) is made smaller. Initial examination shows that even if we assume an order of magnitude decrease in funding, we obtain \\( \alpha = .33  \to \epsilon = (.47, -.32) \\).

### Case 2: OI Long < OI Short

#### Summary

When \\( \mathrm{OI}\_{imb} = \mathrm{OI}\_l - \mathrm{OI}\_s < 0 \\), traders who want to earn yield on their OVL can 1x long OVL-ETH on Overlay with half of their OVL position while selling the other half into ETH. Their aggregate "portfolio" will grow in OVL terms through continuous funding payments to second order in price changes. Thus, traders who prefer to denominate **in OVL terms** and wish to increase their OVL balance will complete for these funding payments until \\( \mathrm{OI}\_{imb} \to 0 \\).

#### The Setup

Assume now that \\( \mathrm{OI}\_{imb} = \mathrm{OI}\_l - \mathrm{OI}\_s < 0 \\), so shorts outweigh longs. Traders who prefer to make yield on their OVL will compete to lock in funding payments.


#### Portfolio Construction

Again we make a relatively simple trade to lock in funding. If we have \\( n \\) OVL to start, we take out a 1x long position on the Overlay OVL-ETH market with \\( n / 2 \\) staked and swap \\( n / 2 \\) for ETH on the spot market. Because this trader prefers OVL, we care about our cost, value, and PnL in OVL terms.

Cost to enter the trade **in OVL terms** is

\\[ C = n \\]

Payoff for the 1x long is

\\[ \mathrm{PO}(t) = \frac{n}{2} \cdot \bigg[ 1 + \frac{P(t) - P_0}{P_0} \bigg] \\]

and value of the spot ETH in OVL terms at time \\( t\\) is \\( (n / 2) \cdot (P_0 / P(t)) \\). Value of the portfolio at \\( t \\) is then

\\[ V(t) = \frac{n}{2} \cdot \bigg[\frac{P_0}{P_k} + 1 + \frac{P(t) - P_0}{P_0} + 2\sum_{i=0}^{m} \frac{\mathrm{FP}(t_i)}{n} \bigg] \\]

Going through the same exercise as in the previous case with \\( P(t) = P_0 \cdot (1 + \epsilon) \\) gives our PnL of

\\[ \mathrm{PnL}(t_i) = \frac{n}{2} \cdot \bigg[ 2\sum_{i=0}^{m} \frac{\mathrm{FP}(t_i)}{n} + \frac{\epsilon ^2}{1 + \epsilon} \bigg] \\]

which is always profitable in OVL terms (in the worst-case scenario of no funding payments and no price movement, PnL = 0).  


## Public Strategies

What's even more interesting is these are simple trades that anyone should be able to participate in. We can code and propose strategies for [yearn vaults](https://github.com/iearn-finance/yearn-vaults) that accomplish this: one to earn yield on OVL and the other to earn yield on ETH. This ultimately stabilizes our system even more given TVL for yearn has ranged from [$500M - $1B](https://defipulse.com/yearn.finance) as of Feb 2021. Although gas costs would likely be difficult to manage. The alternative would be to open source Python bots that anyone can run on their own servers, like [Hummingbot](https://hummingbot.io/) strategies.


# Considerations

## Setting \\( k \\)

We will explore the required value of \\( k \\) in more depth in [risk to the system](note-4). However, for now we note that (assuming no trades are made) the next value of the imbalance, calculated after funding, satisfies the recurrence relation  \\( \mathrm{OI}\_{imb}(m+1) = \mathrm{OI}\_{imb}(m)(1 -2k)\\). This may easily be solved, yielding

\\[ \mathrm{OI}\_{imb}(m) = \mathrm{OI}\_{imb}(0)\cdot \bigg(1 -2k\bigg)^m  \\]

If we define \\( 0 < \ell < 1 \\) such that

\\[ \mathrm{OI}\_{imb}(m) = \ell \cdot \mathrm{OI}\_{imb}(0)\\]

<!-- NOTE: \ell \cdot was on wrong side of eqn -->

then we can explictly solve for \\(k \\) as a function of \\( \ell, m\\). The below gives a table where the leftmost column is \\( \ell \\), and values of \\( m \\) from 1 through 9 are given. Intuitively, it tells us what value of \\( k \\) we need to pick in order to have \\( \ell \\) imbalance left after \\( m \\) funding payments.

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

The risk of an OVL-ETH death spiral still exists when incorporating funding payments, even with a profitable portfolio for case 2. If there is complete loss of faith in OVL and the price collapses while shorts heavily outweigh longs on the OVL-ETH feed, there may be few traders willing to earn yield in OVL and thus take the long side of the trade, even though funding payments would be extremely profitable in OVL terms. Shorts could ultimately still win in the short term, mint more OVL, then cash out that OVL, suppressing the price more and having even more shorts win. It is a positive feedback loop that needs to be mitigated.

This death spiral scenario can be curbed by the introduction of caps on open interest *along with* having contract payoffs be linear. To understand why, assume the OVL-ETH market is completely imbalanced to the short side and no one is willing to go long. Ignore funding payments that would be received by any new long entrants and charged to the shorts for the extreme bound. What is the maximum amount of OVL the system can print given all notional is short the OVL-ETH market?

Simplify and assume all the open interest on the short side is locked in at some average price \\( P_0 \\). The profit/loss **in OVL** at time \\( t \\) to be paid out by the protocol due to this aggregate net short on the OVL-ETH market is

\\[ \mathrm{PnL}(t) = \mathrm{OI}_s \cdot \bigg[1 - \frac{P(t)}{P_0} \bigg] \\]

The maximum amount of OVL the protocol could print occurs when \\( P(t) \to 0 \\), which means

\\[ \mathrm{PnL}\|\_{\mathrm{max}} = \mathrm{OI}_s \\]

for the entire short side. Thus, since we use linear payoffs, the shorts can only cause the system to print an additional 1x the total notional amount imposed in the worst case scenario. Capping the open interest allowed on a market on either side \\( (\mathrm{OI}\_{l}, \mathrm{OI}\_{s}) \\) then implicitly restricts this positive feedback loop scenario to printing a *finite and calculable* amount of OVL even if the price hits zero, removing any worries of an infinite printing death spiral. The additional benefit of introducing per-market caps would be the ability to introduce new markets in incremental steps, increasing caps the more confidence we have that the market empirically tracks our risk expectations.
