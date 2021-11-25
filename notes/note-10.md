---
note: 10
oip-num: 1
title: Cost of Attack - Balancer V2
status: WIP
author: Michael Feldman (@mikeyrf)
discussions-to: oip-1
created: 2021-11-24
updated: N/A
---

Two issues to address with this note:

- What is the cost to attack an Overlay market that uses Balancer V2 price oracles, if the attacker manipulates the spot pool?

- How do we prevent this type of spot manipulation attack?


## Context

Balancer V2 is the only existing AMM that offers *both* historical snapshots of price and liquidity accumulator values queryable on-chain and a deterministic liquidity profile. The combination of these two makes it possible for us to offer a reliable market on their geometric TWAP oracles, as we can use the liquidity oracle to adjust our open interest caps such that the spot manipulation trade is not profitable.

The backrunning trade works like so:

1. Alice takes out an Overlay position on the Balancer V2 spot TWAP feed
2. Alice swaps tokens through the spot pool for \\( \nu \\) blocks to increase/decrease price in her Overlay position's favor
3. Alice exits the Overlay position

Total profit for the attack is the gain obtained from the Overlay position less the loss to slippage from the swaps on spot.

My prior note examining [cost of attack for Uniswap V2 TWAPs](note-2) incorrectly assumed that the attacker loses all capital used to swap on spot for the manipulation. In reality, the attacker only loses to slippage as they receive tokens out from the spot pool. The difference in capital required to execute the attack becomes apparent when the attacker manipulates the pool over multiple blocks within the averaging window (little is lost to slippage) vs over just one block (most is lost to slippage).

I'll use this note for a more proper derivation of cost of attack and an implementable, via our market contracts, mitigation strategy to make this attack unprofitable in all reasonable instances.


## Balancer Math

From the [Balancer whitepaper](https://balancer.fi/whitepaper.pdf), the invariant \\( V \\) for each spot pool is

\\[ V = \prod_{k} B_k^{w_k} \\]

where

- \\( B_k \\) is the number of \\( k \\) type tokens in the pool
- \\( w_k \\) is the weight for \\( k \\) type tokens in the pool

The spot price inferred from the relative number of tokens in the pool is

\\[ SP_i^o = \frac{B_i}{B_o} \cdot \frac{w_o}{w_i} \\]

with \\( i \\) type tokens as the quote and \\( o \\) type tokens as the base currency.

The number of quote tokens \\( A_i \\) need to swap into the pool to move the price from \\( SP^o_i \to SP^{\prime o}_i \\) and the number of base tokens \\( A_o \\) received out from said swap are found to be

\\[ A_i = B_i \cdot \bigg[ \bigg( \frac{SP^{\prime o}_i }{SP^o_i} \bigg)^{\frac{w_o}{w_o+w_i}} - 1 \bigg] \\]
\\[ A_o = B_o \cdot \bigg[ 1 - \bigg( \frac{SP^{\prime o}_i }{SP^o_i} \bigg)^{-\frac{w_i}{w_o+w_i}} \bigg] \\]

The Balancer oracle reports the geometric TWAP

\\[ SP_i^o(t_1, t_2) = \bigg( \prod_{k=t_1}^{t_2} SP_i^o(k) \bigg)^{\frac{1}{t_2-t_1}} \\]

given the accumulator value is stored as the sum of the logarithm of price.


## Overlay Math

For a user that takes out a position with open interest \\( \mathrm{OI} \\) at an entry price of \\( P(i) \\), their position's PnL is

\\[ \mathrm{PnL}(t) = \pm \mathrm{OI} \cdot \bigg[ \frac{P(t)}{P(i)} - 1 \bigg] \\]

where \\( \pm = +1 \\) if long and \\( \pm = -1 \\) if short. The open interest attributed to a position at entry is

\\[ \mathrm{OI} = N \cdot L \\]

for a collateral amount deposited \\( N \\) and a leverage choice \\( L \\). The debt the user owes to the system is \\( D = N \cdot (L - 1) \\).

To combat a trader who attempts to front-run the information lag inherent in the manipulation-resistant oracle value used by the Overlay market vs the "real" spot value, we added a [bid-ask spread and market impact](note-8) to all trades on the platform. The price ratio \\( P(t) / P(i) \\) effectively becomes

\\[ \frac{P(t)}{P(i)} = e^{x \mp 2\delta } \\]

where

- \\( \delta \\) is a static spread
- \\( \mp = -1 \\) for longs and \\( \mp = +1 \\) for shorts

The trader pays an upfront impact fee on position size, but for a position built up over a long enough time horizon (e.g. effectively "TWAPing" in), this fee can trend to zero.


## Backrunning Trade

For the backrunning trade, we assume

- Market impact fees are zero, taking the limit of a trader slowly entering into their Overlay position prior to manipulating spot
- Trading fees are zero and ignore gas costs
- Arbitrageurs bring the spot price on Balancer back from \\( SP^{\prime o}_i \to SP^o_i \\) at the beginning of each successive block, after the accumulator registers the manipulated price \\( SP^{\prime o}_i \\)

The attacker manipulates the spot price from \\( SP^o_i \to SP^{\prime o}_i \\).

To profitably execute the attack, the attacker must overcome the static spread applied to entry and exit prices on the Overlay position. PnL for the attack is

\\[ \mathrm{PnL}\_{\textrm{attack}} = \mathrm{PnL}\_{\textrm{Overlay}} + \mathrm{Slippage}\_{i \to o} \\]

where

- \\( \mathrm{PnL}\_{\textrm{Overlay}} \\) is the profit from the Overlay leg of the trade
- \\( \mathrm{Slippage}\_{i \to o} \\) are the funds lost to slippage on the spot leg

As arbitrageurs bring the spot price back, the value of the tokens received by the attacker from the spot pool is \\( SP^o_i A_o \\). The capital lost to slippage is then given by

$$\begin{eqnarray}
\mathrm{Slippage}_{i \to o} &=& SP^o_i A_o - A_i \\
&=& B_i \cdot \bigg\{\frac{w_o}{w_i} \cdot \bigg[ 1 - \bigg( \frac{SP^{\prime o}_i }{SP^o_i} \bigg)^{-\frac{w_i}{w_o+w_i}} \bigg] - \bigg( \frac{SP^{\prime o}_i }{SP^o_i} \bigg)^{\frac{w_o}{w_o+w_i}} + 1 \bigg\}
\end{eqnarray}$$
