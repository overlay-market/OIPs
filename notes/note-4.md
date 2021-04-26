---
note: 4
oip-num: 1
title: Risk and the Funding Constant
status: WIP
author: Michael Feldman (@mikeyrf)
discussions-to: oip-1
created: 2021-03-08
updated: N/A
---

Two issues to address with this note:

- What should we set the constant \\( k \\) to be in each of our funding payments?

- How is \\( k \\) related to the risk a market feed adds to the system?


## Context

[Funding payments](note-1) are meant to incentivize a balanced set of positions on each market offered by the protocol so that passive OVL holders, who effectively act as the counterparty to all unbalanced trades in the system, are protected from significant unexpected dilution. This ensures the supply of the settlement currency (OVL) remains relatively stable over longer periods of time -- stable in the sense of governance having the ability to predict the expected worst case inflation rate within a certain degree of confidence due to unbalanced trades on markets.

For better or for worse, governance is given the ability to tune the rate \\( k \\) at which funding flows from longs to shorts or shorts to longs to balance the open interest on a market over time. The purpose of this note is to provide guidance on what to set the value of \\( k \\) to.

As \\( k \\) is the rate at which open interest on a market rebalances, it is directly linked with the time it takes to draw down the risk associated with an imbalanced book. Thus, we suggest \\( k \\) be related to the risk the underlying feed adds to the system and inherently passive OVL holders through the currency supply.

### Background

Return to the functional form of our funding payments

\\[ \mathrm{FP} (t) = k \cdot \mathrm{OI}\_{imb}(t) \\]

where \\( {\mathrm{OI}\_{imb}} (t) = {\mathrm{OI}_l} (t) - {\mathrm{OI}_s} (t) \\) is the open interest imbalance between the long \\( l \\) and short \\( s \\) side on a market at time \\( t \\).

We define position \\( j \\)'s contribution to the open interest on side \\( a \in \\{ l, s \\} \\) as the product of the OVL collateral locked \\( N_{ja} \\) and leverage used \\( L_{ja} \\). The total open interest on a side is the sum over all positions:

\\[ \mathrm{OI}_a (t) = \sum\_{j} N\_{ja} L\_{ja}  \\]

Funding payments are made from longs to shorts when \\( \mathrm{OI}\_l > \mathrm{OI}\_s \\), and shorts to longs when \\( \mathrm{OI}\_l < \mathrm{OI}\_s \\). These are paid out intermittently at every oracle fetch \\( i \in \\{ 0, 1, ..., m \\} \\) between time \\( 0 \\) and \\( t \\).

For this note, consider the case where \\( \mathrm{OI}_{imb} > 0 \\) so longs outweigh shorts. Our results will be the same when \\( {\mathrm{OI}}\_{imb} < 0 \\).

For further simplicity, assume no more positions are built or unwound on either side such that the total open interest remains a constant: \\( \mathrm{OI}_l + \mathrm{OI}_s = \mathrm{const} \\). The latter assumption will skew our risk estimates, but likely to the more conservative side as funding incentives should trend towards a more balanced book. It also allows us to map time 1:1 with each discrete oracle fetch \\( t = i \\).


## Risk-Based Approach to Balancing Markets

### Imbalance Over Time

What does the evolution of the imbalance look like when we factor in funding payments up to fetch \\( m \\)? In terms of the prior period \\( m-1 \\), open interest on the long side after paying funding will be

\\[ {\mathrm{OI}\_{l}} (m) = {\mathrm{OI}\_{l}}(m-1) - \mathrm{FP}(m-1) \\]

and short side after receiving funding

\\[ {\mathrm{OI}\_{s}} (m) = {\mathrm{OI}\_{s}}(m-1) + \mathrm{FP}(m-1) \\]

Subtracting the two and expanding \\( \mathrm{FP}(m-1) \\) gives the time evolution of the imbalance from \\( m-1 \\) to \\( m \\)

\\[ {\mathrm{OI}\_{imb}}(m) = {\mathrm{OI}\_{imb}} (m-1) \cdot \bigg( 1 - 2k \bigg) \\]

Rinse and repeat \\( m \\) times to get the time evolution as a function of the open interest imbalance when traders initially enter their positions

\\[ {\mathrm{OI}\_{imb}} (m) = {\mathrm{OI}\_{imb}}(0) \cdot \bigg( 1 - 2k \bigg)^m \\]

where \\( k \in [0, \frac{1}{2}] \\).


### Risk to the System

One can view the risk to the system at time \\( t = 0 \\) due to the long imbalance created on this market as the expected PnL the system would need to pay out to a long position with notional \\( {\mathrm{OI}_{imb}} (0) > 0 \\) at some time in the future \\( t = m \\):

\\[ \mathrm{PnL} (m) = {\mathrm{OI}\_{imb}} (m) \cdot \bigg[ \frac{P (m)}{P(0)} - 1 \bigg] \\]

where \\( P(i) \\) is the market value fetched from the oracle at time \\( i \\). An easy way to arrive at this is to sum the unrealized PnL at time \\( m \\) of all the long *and* short positions that have each been built at time \\( 0 \\).

Take \\( P : \Omega \to \mathbb{R} \\) to be a random variable on the probability space \\( (\Omega, \mathcal{F}, \mathrm{P}) \\) driven by a stochastic process \\( W_t \\)

\\[ P(t) = P(0) e^{\mu t + \sigma W_t} \\]

Assume the feed exhibits [Geometric Brownian motion (GBM)](https://en.wikipedia.org/wiki/Geometric_Brownian_motion) such that \\( W_t \\) is a Wiener process, with a word of caution: DeFi price feeds will likely be fat-tailed, so governance should be more conservative with \\( k \\) values chosen.

PnL to be minted/burned at time \\( m \\) for this hypothetical long position reduces to

\\[ \mathrm{PnL} (m) = {\mathrm{OI}\_{imb}}(0) \cdot d^{-m} \cdot \bigg[ e^{\mu m T + \sigma W\_{m T}}  - 1 \bigg] \\]

where \\( T \\) is the length of time between funding payments and

\\[ d \equiv \frac{1}{1 - 2k} \\]

with \\( d \in \[ 1, \infty \) \\). In terms of \\( l \\) from [note 1](https://oips.overlay.market/notes/note-1), \\( l(m) = d^{-m} \\).

The protocol itself is liable for this imbalance PnL. Our approach to minimizing the risk borne by passive OVL holders will be to choose a \\( k \\) that substantially reduces the expected payout due to positional imbalance within a finite number of time intervals \\( m \\), assuming an acceptable confidence level \\( \alpha \\).

### Limiting Behavior

First, let's put bounds on \\( k \\) based on the long-run behavior we wish to enforce. \\( k \\) should be chosen such that a market's risk to the system will be reduced to almost nothing the more time that passes by.

This translates to two potential requirements over longer time horizons:

1. [Expected value](https://en.wikipedia.org/wiki/Expected_value) of the imbalance PnL should approach zero:
\\[ \lim_{m \to \infty} \mathbb{E}[ \mathrm{PnL}(m) \| \mathcal{F}_{m} ] = 0 \\]

2. [Value at risk](https://en.wikipedia.org/wiki/Value_at_risk) to the system due to the imbalance should approach zero:
\\[ \lim_{m \to \infty} \mathrm{VaR}_{\alpha}(m) = 0 \\]

where we define our market's value at risk metric to be the maximum amount of excess OVL we expect the system to print at some future time \\( m \\), with a given level of certainty \\( \alpha \\).

Mathematically,

\\[ 1 - \alpha = \mathbb{P}[ \mathrm{PnL}(m) \leq \mathrm{VaR}_{\alpha}(m) ] \\]

where \\( 1 - \alpha \\) is the probability the imbalance PnL is less than an amount \\( \mathrm{VaR}_{\alpha}(m) \\) at time \\( m \\). VaR estimates can be found through this expression.

#### Expected Value

The expected value of the imbalance PnL at time \\( m \\) is

\\[ \mathbb{E}[ \mathrm{PnL}(m) \| \mathcal{F}_{m} ] = \mathrm{OI}\_{imb}(0) \cdot d^{-m} \cdot \bigg[ \bigg(e^{(\mu + \sigma^2 / 2) T} \bigg)^m - 1 \bigg] \\]

using the linearity of the expectation and the identity \\( \mathbb{E}[ e^{\sigma W_{t}} \| \mathcal{F}_{t} ] = e^{\frac{\sigma^2 t}{2}} \\) for GBM. Over longer time horizons, the expected value to be paid out by the protocol will approach zero when

\\[ d > e^{(\mu + \sigma^2 / 2)T} \\]

This condition requires that, per funding interval, the decay in open interest imbalance \\( d^{-1} \\) outpace the expected drift in market price \\( \mathbb{E}[ \frac{P(i)}{P(i-1)} \| \mathcal{F}_{i} ] \\).


#### Value at Risk

Expanding further, we can examine the value at risk (VaR) to the system for paying out PnL on this hypothetical long position due to our market's imbalance. Note, the protocol and passive OVL holders are taking the other side, so what we really want is the probability \\( 1 - \alpha \\) this imbalance PnL is less than an amount \\( \mathrm{VaR}_{\alpha, n} \\):

\\[ 1 - \alpha = \mathbb{P}[ {\mathrm{PnL}\_{imb}}\_n \leq \mathrm{VaR}_{\alpha, n} ] \\]

where we abuse notation here given the [usual definition of VaR](https://en.wikipedia.org/wiki/Value_at_risk). From the prior section,

\\[ 1 - \alpha = \mathbb{P}\bigg[{\mathrm{OI}\_{imb}}\_{0} \cdot a^{-n} \cdot \bigg( e^{\mu \cdot n \cdot T + \sigma \cdot W\_{n \cdot T}}  - 1 \bigg) \leq \mathrm{VaR}_{\alpha, n} \bigg] \\]

which reduces to

\\[ 1 - \alpha = \Phi \bigg( \frac{1}{\sigma \cdot \sqrt{n \cdot T}} \cdot \bigg[ \ln \bigg( 1 + a^{n} \cdot \tilde{\mathrm{VaR}}_{\alpha, n} \bigg) - \mu \cdot n \cdot T \bigg] \bigg) \\]

\\( \tilde{\mathrm{VaR}}_{\alpha, n} = \frac{\mathrm{VaR}\_{\alpha, n}}{ {\mathrm{OI}\_{imb}}\_{0} } \\) is normalized for the original imbalance amount and \\( \Phi (z) = \mathbb{P}[ Z \leq z ] \\) is the CDF of the standard normal distribution \\( Z \sim \mathcal{N}(0, 1) \\). Inverting this, one finds the normalized upper bound for the PnL to be paid out \\( n \\) blocks in the future, \\( \tilde{\mathrm{VaR}}\_{\alpha, n} \\), as a function of the (\\( 1 - \alpha \\))-quantile:

\\[ \tilde{\mathrm{VaR}}_{\alpha, n} = a^{-n} \cdot \bigg[ e^{\mu \cdot n \cdot T + \sigma \cdot \sqrt{n \cdot T} \cdot {\Phi}^{-1}(1-\alpha)} - 1 \bigg] \\]

Anticipated VaR to the system also scales with \\( a^{-n} \\), supporting a choice of \\( a \gg e^{(\mu + \sigma^2 / 2) \cdot T} \\). Similar to the analysis above, we want VaR to decrease over time as more blocks go by, such that the limit approaches zero as \\( n \to \infty \\). This puts a lower bound on acceptable values for \\( b \\).

Substituting for \\( a \\),

\\[ \tilde{\mathrm{VaR}}_{\alpha, n} = \frac{1}{b^{n}} \cdot \frac{e^{\sigma \cdot \sqrt{n \cdot T} \cdot {\Phi}^{-1}(1-\alpha)}}{e^{\frac{\sigma^2}{2} \cdot n \cdot T}} - \frac{1}{a^{n}} \\]

The first term is what we need to worry about, tuning \\( b \\) such that it appropriately decays to zero for large \\( n \\). Notice, since \\( n \geq 0 \\),

\\[ \frac{1}{b^{n}} \cdot \frac{e^{\sigma \cdot \sqrt{n \cdot T} \cdot {\Phi}^{-1}(1-\alpha)}}{e^{\frac{\sigma^2}{2} \cdot n \cdot T}} \leq \bigg( \frac{1}{b} \cdot \frac{e^{\sigma \cdot \sqrt{T} \cdot {\Phi}^{-1}(1-\alpha)}}{e^{\frac{\sigma^2}{2} \cdot T}} \bigg)^n \\]

which means having the right-hand side of this inequality go to zero for \\( n \to \infty \\) will lead to the first term in our expression for VaR also approaching zero. This occurs when the term in parentheses on the right-hand side is less than 1 or

\\[ b > e^{\sigma \cdot \sqrt{T} \cdot {\Phi}^{-1}(1-\alpha) - \frac{\sigma^2}{2} \cdot T} \\]

giving us a lower bound on \\( b \\) for a confidence level of \\( 1 - \alpha \\) on our VaR to decay to zero as \\( n \to \infty \\). Let \\( b_{\alpha} = e^{\sigma \cdot \sqrt{T} \cdot {\Phi}^{-1}(1-\alpha) - \frac{\sigma^2}{2} \cdot T} \\). If our chosen value for \\( b >  b_{\alpha} \\), we'll have with confidence \\( 1 - \alpha \\) \\( \lim_{n\to\infty} \tilde{\mathrm{VaR}}_{\alpha, n} = 0 \\).


### Choice of \\( k \\)

The conditions on \\( k \\) imposed above ensure the appropriate limiting behavior as \\( n \to \infty \\), such that funding payments effectively zero out risk to the system over longer time horizons. However, our choice for an exact value of \\( k \\) should be set by our risk tolerance for the amount of OVL we'd be willing to let the system print *over shorter timeframes* if all excess notional causing the imbalance were to unwind at the same time *before* funding is able to fully rebalance the system.

Thus, we wish to ensure the normalized value at risk to the system due to a particular market some finite number of blocks \\( n \\) into the future is equal to a threshold level \\( \tilde{\mathrm{VaR}}_{\alpha, n} = \tilde{\epsilon}\_{\alpha, n} \\) with confidence \\( 1 - \alpha \\). Assume we impose a cap on the notional imbalance on a market at \\( \| {\mathrm{OI}\_{imb}}_0 \| = \mathrm{OI}\_{imb}\|\_{\mathrm{max}} \\), such that no more positions can be built if the notional to be added to the overweight side would cause the cap to be breached (i.e. \\( - \mathrm{OI}\_{imb}\|\_{\mathrm{max}} \leq \mathrm{OI}\_{imb} \leq \mathrm{OI}\_{imb}\|\_{\mathrm{max}} \\)).

Max value at risk for this market \\( n \\) periods into the future is then (still assuming \\( \mathrm{OI}\_{imb} > 0 \\))

\\[ \mathrm{VaR}_{\alpha, n}\|\_{\mathrm{max}} = \tilde{\epsilon}\_{\alpha, n} \cdot \mathrm{OI}\_{imb}\|\_{\mathrm{max}} \\]

and max inflation \\( i_{\alpha, n}\|\_{\mathrm{max}} \\) of the total currency supply \\( \mathrm{TS}_0 \\) produced by this hypothetical amount at risk is

\\[ i_{\alpha, n}\|\_{\mathrm{max}} = \frac{\mathrm{VaR}_{\alpha, n}\|\_{\mathrm{max}}}{\mathrm{TS}_0} = \frac{\tilde{\epsilon}\_{\alpha, n} \cdot \mathrm{OI}\_{imb}\|\_{\mathrm{max}}}{\mathrm{TS}_0} \\]

Take the imbalance cap to be some fixed percentage \\( c_{\mathrm{max}} \in [0, 1] \\) of the total supply such that \\( \mathrm{OI}\_{imb}\|\_{\mathrm{max}} = c_{\mathrm{max}} \cdot \mathrm{TS}_0 \\). Max inflation rate \\( n \\) blocks into the future then reduces to

\\[ i_{\alpha, n}\|\_{\mathrm{max}} = \tilde{\epsilon}\_{\alpha, n} \cdot c_{\mathrm{max}} \\]

showing our chosen threshold risk level \\( \tilde{\epsilon}\_{\alpha, n} \\) is directly proportional to the hypothetical inflation rate we're willing to tolerate with \\( 1 - \alpha \\) confidence for the currency supply (which the cap helps to mitigate). So \\( i_{\alpha, n}\|\_{\mathrm{max}} \\) is ultimately what governance will target.

How does this translate to a value to set for \\( k \\)? Return to the form of our targeted normalized value at risk for the system \\( \tilde{\mathrm{VaR}}_{\alpha, n} = \tilde{\epsilon}]\_{\alpha, n} \\), plug in for the max inflation rate to be tolerated for a market (adjusted for the cap)

\\[ \frac{i_{\alpha, n}\|\_{\mathrm{max}}}{c_{\mathrm{max}}} = a^{-n} \cdot \bigg[ e^{\mu \cdot n \cdot T + \sigma \cdot \sqrt{n \cdot T} \cdot {\Phi}^{-1}(1-\alpha)} - 1 \bigg] \\]

Solving for \\( a = a_{\alpha, n} \\) gives a guideline for our governance-set funding constant based on a tolerated inflation rate within \\( n \\) blocks due to the market at \\( 1-\alpha \\) confidence

\\[ a_{\alpha, n} = \bigg[ \frac{c_{\mathrm{max}}}{i_{\alpha, n}\|\_{\mathrm{max}}} \cdot \bigg( e^{\mu \cdot n \cdot T + \sigma \cdot \sqrt{n \cdot T} \cdot {\Phi}^{-1}(1-\alpha)} - 1 \bigg) \bigg]^{1/n} \\]

where \\( k_{\alpha, n} = \frac{1}{2} \cdot [ 1 - \frac{1}{a_{\alpha, n}} ] \\), with target conditions to ensure \\( \lim_{n\to\infty} \tilde{\mathrm{VaR}}\_{\alpha, n} = 0 \\)

\\[ \frac{i_{\alpha, n}\|\_{\mathrm{max}}}{c_{\mathrm{max}}} < 1 - e^{-n \cdot ( \mu \cdot T + \sigma \cdot \sqrt{T} \cdot \Phi^{-1} (1 - \alpha) )} \\]

and \\( \lim_{n\to\infty} \mathbb{E}[ {\mathrm{PnL}\_{imb}}\_n \| \mathcal{F}_{n} ] = 0 \\)

\\[ \frac{i_{\alpha, n}\|\_{\mathrm{max}}}{c_{\mathrm{max}}} < e^{-\sigma^2 \cdot n \cdot T / 2} \cdot \bigg[ e^{\sigma \cdot \sqrt{n \cdot T} \cdot \Phi^{-1} (1 - \alpha)} - e^{-n \cdot \mu \cdot T} \bigg] \\]


### Determining \\( \mu \\) and \\( \sigma^2 \\)

We'll use maximum likelihood estimation (MLE) from on-chain samples to find our \\( \mu \\) and \\( \sigma^2 \\) values. At launch, we should have these simply inform our chosen \\( k \\) values over rolling time periods versus automating completely, and allow governance to tweak funding rates given existing risk conditions.

Assume \\( T \\) is the `periodSize` of a [sliding window TWAP oracle](note-2), such that funding is paid upon every price update of an Overlay market. Let

\\[ R(i) = \ln \bigg[ \frac{P(i)}{P(i-1)} \bigg] = \mu T + \sigma [ W_{i T} - W_{(i-1) T} ] \sim \mathcal{N}(\mu T, \sigma^2  T) \\]

Sampling \\( N+1 \\) of these windows over a length of time \\( (N + 1) \cdot T \\) gives \\( (r_1, r_2, ..., r_{N}) \\) values of \\( R \\) with MLEs

\\[ \hat{\mu} = \frac{1}{N \cdot T} \sum_{i = 1}^N r_i \\]

and

\\[ \hat{\sigma}^2 = \frac{1}{N \cdot T} \sum_{i = 1}^N (r_i - \hat{\mu} T)^2 \\]

to inform our governance-determined value for \\( k \\).


### Concrete Numbers


## Considerations

The analysis above only examines value at risk to the system on an individual market-by-market level. While useful, it is not entirely accurate at the macro level. We should really examine the "portfolio" of markets we're offering and the total value at risk to the system caused by the *sum of imbalances* on each individual market

\\[ 1 - \alpha = \mathbb{P}\bigg[ \sum_{j=1}^{N} {\mathrm{OI}\_{imb}}\_{j} (t_0) \cdot a^{-n}\_{j} \cdot \bigg( e^{\mu_j \cdot n \cdot T + \sigma_j \cdot W\_{n \cdot T}}  - 1 \bigg) \leq \mathrm{VaR}_{\alpha, n} \bigg] \\]

where \\( (\mu_j, \sigma_j, a_j) \\) are the relevant parameters for market \\( j \\) assuming \\( N \\) total markets offered by the protocol.


## Acknowledgments

[Daniel Wasserman](https://github.com/dwasse) for pushing the idea that funding be related to the risk a market feed adds to the system.

<!-- TODO: Should really be looking at "portfolio" of markets we're offering and VaR from combination of feeds! sum of log normals isn't closed form (?) so more annoying. Do this later ... -->
