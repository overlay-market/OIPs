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

[Funding payments](note-1) are meant to incentivize a balanced set of positions on each market offered by the protocol so that passive OVL holders, who effectively act as the counterparty to all unbalanced trades in the system, are protected from significant unexpected dilution. This ensures the supply of the settlement currency (OVL) remains relatively stable over longer periods of time -- stable in the sense of governance having the ability to predict the expected worst case inflation rate with a certain degree of confidence due to unbalanced trades on markets.

For better or worse, governance is given the ability to tune the per-market rate \\( k \\) at which funding flows from longs to shorts or shorts to longs to balance the open interest on a market over time. The purpose of this note is to provide guidance on what to set the value of \\( k \\) to for each individual market.

As \\( k \\) is the rate at which open interest on a market rebalances, it is directly linked with the time it takes to draw down the risk associated with an imbalanced book. Thus, we suggest \\( k \\) be related to the risk the underlying feed adds to the system and inherently passive OVL holders through the currency supply. Different markets will then have different \\( k \\) values, depending on the distributional properties of the underlying feed itself.

### Background

Return to the functional form of our funding payments

\\[ \mathrm{FP} (t) = k \cdot \mathrm{OI}\_{imb}(t) \\]

where \\( {\mathrm{OI}\_{imb}} (t) = {\mathrm{OI}_l} (t) - {\mathrm{OI}_s} (t) \\) is the open interest imbalance between the long \\( l \\) and short \\( s \\) side on a market at time \\( t \\).

We define position \\( j \\)'s contribution to the open interest on side \\( a \in \\{ l, s \\} \\) as the product of the OVL collateral locked \\( N_{aj} \\) and leverage used \\( L_{aj} \\). The total open interest on a side is the sum over all positions:

\\[ \mathrm{OI}_a (t) = \sum\_{j} N\_{aj} L\_{aj}  \\]

Funding payments are made from longs to shorts when \\( \mathrm{OI}\_l > \mathrm{OI}\_s \\), and shorts to longs when \\( \mathrm{OI}\_l < \mathrm{OI}\_s \\). These are paid out intermittently at discrete intervals \\( i \in \\{ 0, 1, ..., m \\} \\) between time \\( 0 \\) and \\( t \\).

For this note, consider the case where \\( \mathrm{OI}_{imb} > 0 \\) so longs outweigh shorts. Our results will be the same when \\( {\mathrm{OI}}\_{imb} < 0 \\).

For further simplicity, assume no more positions are built or unwound on either side such that the total open interest remains a constant: \\( \mathrm{OI}_l + \mathrm{OI}_s = \mathrm{const} \\). The latter assumption will skew our risk estimates, but likely to the more conservative side as funding incentives should trend towards a more balanced book.


## Risk-Based Approach to Balancing Markets

### Imbalance Over Time

What does the evolution of the imbalance look like when we factor in funding payments up to interval \\( m \\)? In terms of the prior period \\( m-1 \\), open interest on the long side after paying funding will be

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

where \\( P(i) \\) is the market value fetched from the oracle at interval \\( i \\), abusing notation in mapping \\( t=i \\) to the time at interval \\( i \\). An easy way to arrive at this is to sum the unrealized PnL at time \\( m \\) of all the long *and* short positions that have each been built at time \\( 0 \\).

Take \\( P : \Omega \to \mathbb{R} \\) to be a random variable on the probability space \\( (\Omega, \mathcal{F}, \mathrm{P}) \\) driven by a stochastic process \\( W_t \\)

\\[ P(t) = P(0) e^{\mu t + \sigma W_t} \\]

Assume the feed exhibits [Geometric Brownian motion (GBM)](https://en.wikipedia.org/wiki/Geometric_Brownian_motion) such that \\( W_t \\) is a Wiener process, with a word of caution: DeFi price feeds will likely be fat-tailed, so governance should be more conservative with \\( k \\) values chosen.

PnL to be minted/burned at time \\( m \\) for this hypothetical long position reduces to

\\[ \mathrm{PnL} (m) = {\mathrm{OI}\_{imb}}(0) \cdot d^{-m} \cdot \bigg[ e^{\mu m T + \sigma W\_{m T}}  - 1 \bigg] \\]

where \\( T \\) is the average length of time between intervals and we define

\\[ d \equiv \frac{1}{1 - 2k} \\]

with \\( d \in \[ 1, \infty \) \\). In terms of \\( l \\) from [note 1](note-1), \\( l(m) = d^{-m} \\).

The protocol itself is liable for this imbalance PnL. Our approach to minimizing the risk borne by passive OVL holders will be to choose a \\( k \\) that substantially reduces the expected payout due to positional imbalance within a finite number of time intervals \\( m \\), assuming an acceptable level of uncertainty \\( \alpha \\).

### Limiting Behavior

First, let's put bounds on \\( k \\) based on the long-run behavior we wish to enforce. \\( k \\) should be chosen such that a market's risk to the system will be reduced to almost nothing the more time that passes by.

This translates to two potential requirements over longer time horizons:

1. [Expected value](https://en.wikipedia.org/wiki/Expected_value) of the imbalance PnL should approach zero:
\\[ \lim_{m \to \infty} \mathbb{E}[ \mathrm{PnL}(m) \| \mathcal{F}_{m} ] = 0 \\]

2. [Value at risk](https://en.wikipedia.org/wiki/Value_at_risk) to the system due to the imbalance should approach zero:
\\[ \lim_{m \to \infty} \mathrm{VaR}_{\alpha}(m) = 0 \\]

where we define our market's value at risk metric to be the worst case amount of excess OVL we expect the system to print at some future time \\( m \\), with a given level of uncertainty \\( \alpha \\).

Formally,

\\[ 1 - \alpha = \mathbb{P}[ \mathrm{PnL}(m) \leq \mathrm{VaR}_{\alpha}(m) ] \\]

where \\( 1 - \alpha \\) is the probability the imbalance PnL is less than an amount \\( \mathrm{VaR}_{\alpha}(m) \\) at time \\( m \\). VaR estimates can be found through this expression.

#### Expected Value

The expected value of the imbalance PnL at time \\( m \\) is

\\[ \mathbb{E}[ \mathrm{PnL}(m) \| \mathcal{F}_{m} ] = \mathrm{OI}\_{imb}(0) \cdot d^{-m} \cdot \bigg[ \bigg(e^{(\mu + \sigma^2 / 2) T} \bigg)^m - 1 \bigg] \\]

using the linearity of the expectation and the identity \\( \mathbb{E}[ e^{\sigma W_{t}} \| \mathcal{F}_{t} ] = e^{\frac{\sigma^2 t}{2}} \\) for GBM. Over longer time horizons, the expected value to be paid out by the protocol will approach zero when

\\[ d > e^{(\mu + \sigma^2 / 2)T} \\]

This condition requires that, per funding interval, the decay in open interest imbalance \\( d^{-1} \\) outpace the expected drift in market price \\( \mathbb{E}[ \frac{P(i)}{P(i-1)} \| \mathcal{F}_{i} ] \\).


#### Value at Risk

Our value at risk metric due to a market's open interest imbalance can be found from the assertion that \\( 1-\alpha \\) be the probability the imbalance PnL is less than the VaR amount at time \\( m \\). After some manipulation, the more formal expression for \\( \mathbb{P}[ \mathrm{PnL}(m) \leq \mathrm{VaR}_{\alpha}(m) ] \\) becomes

\\[ 1 - \alpha = \Phi \bigg( \frac{1}{\sigma \sqrt{m T}} \cdot \bigg[ \ln \bigg( 1 + d^{m} \cdot \frac{\mathrm{VaR}\_{\alpha}(m)}{\mathrm{OI}\_{imb}(0)} \bigg) - \mu m T \bigg] \bigg) \\]

where \\( \Phi (z) = \mathbb{P}[ Z \leq z ] \\) is the [CDF](https://en.wikipedia.org/wiki/Cumulative_distribution_function) of the standard normal distribution \\( Z \sim \mathcal{N}(0, 1) \\). We've also used the normality of [Wiener process](https://en.wikipedia.org/wiki/Wiener_process) increments \\( W_{t+\tau} - W_t \sim \mathcal{N}(0, \tau) \\). In terms of VaR,

\\[ \mathrm{VaR}\_{\alpha} (m) = \mathrm{OI}\_{imb}(0) \cdot d^{-m} \cdot \bigg[ e^{\mu m T + \sigma \sqrt{m T} \cdot {\Phi}^{-1}(1-\alpha)} - 1 \bigg] \\]

which is, with probability \\( 1-\alpha \\), the worst case amount of excess OVL the system is likely to print by time \\( m \\), given initial imbalance state \\( \mathrm{OI}\_{imb}(0) \\).

As \\( m \to \infty \\), VaR will approach zero when

\\[ d^m > e^{\mu m T + \sigma \sqrt{mT} \cdot \Phi^{-1}(1-\alpha)} \\]

The choice of \\( \alpha \\) dictates how large the lower bound on \\( d \\) is vs the expected value condition.


### Choice of \\( k \\)

The conditions on our per-market parameter \\( k \\) imposed above ensure the appropriate limiting behavior as \\( m \to \infty \\): funding payments effectively zero out risk to the system over longer time horizons. However, our choice for an exact value of \\( k \\) for each market should be set by our risk tolerance for the amount of OVL we'd be willing to let the system print *over shorter timeframes*, if all excess notional causing the imbalance were to unwind at the same time *before* funding is able to fully rebalance trades on the market.

This translates to setting a market's \\( k \\) value such that the maximum value at risk to the system due to trading on the market, some finite number of blocks \\( m \\) into the future, is equal to a threshold level \\( V\_{\alpha, m} \\) with confidence \\( 1 - \alpha \\). Assume we impose a cap \\( C \\) on the notional allowed on either side of a market

\\[ \mathrm{OI}_a (t) \leq C  \\]

where \\( a \in \\{ l, s \\} \\). The initial state \\( \\{ \mathrm{OI}\_{l}(0), \mathrm{OI}\_{s}(0) \\} \\) that causes the maximum value at risk to the system is one in which the initial imbalance is largest: i.e., when there's zero notional on one of the sides and the other side has notional equal to the cap. Then, the magnitude of the initial imbalance will also equal the cap \\( \|\mathrm{OI}\_{imb}(0)\| = C \\), when value at risk to the system is greatest. Our maximum value at risk to the system \\( \mathrm{VaR}\_{\alpha, max} (m) \\) at some time \\( m \\) in the future becomes

\\[ \mathrm{VaR}\_{\alpha, max} (m) = C \cdot d^{-m} \cdot \bigg[ e^{\mu m T + \sigma \sqrt{m T} \cdot {\Phi}^{-1}(1-\alpha)} - 1 \bigg] \\]

Setting \\( \mathrm{VaR}\_{\alpha, max} (m) \\) to our threshold level and manipulating

\\[ d = \bigg\\{ \frac{C}{V_{\alpha, m}} \cdot \bigg[ e^{\mu m T + \sigma \sqrt{m T} \cdot {\Phi}^{-1}(1-\alpha)} - 1 \bigg] \bigg\\}^{1/m} \\]

gives an expression for \\( d \\) (and \\( k \\)) in terms of the cap chosen \\( C \\) and the threshold amount of OVL \\( V_{\alpha, m} \\) we'd be willing to allow this market to print within \\( m \\) time periods. Thus, we are able to constrain the worst case rate of inflation due to the imbalance on this market with confidence \\( 1 - \alpha \\) simply by setting and updating \\( d \\) accordingly.

Requiring \\( \mathrm{VaR} \to 0 \\) for large \\( m \\) bounds the value for the threshold level with respect to the cap

\\[ \frac{C}{V\_{\alpha, m}} > 1 \\]


### Determining \\( \mu \\) and \\( \sigma^2 \\)

We can use maximum likelihood estimation (MLE) from on-chain samples to find our GBM \\( \mu \\) and \\( \sigma^2 \\) values. Assume \\( T \\) is the `periodSize` of a [sliding window TWAP oracle](note-2). Let

\\[ R(i) = \ln \bigg[ \frac{P(i)}{P(i-1)} \bigg] = \mu T + \sigma [ W_{i T} - W_{(i-1) T} ] \sim \mathcal{N}(\mu T, \sigma^2  T) \\]

Sampling \\( N+1 \\) of these periods over a length of time \\( (N + 1) \cdot T \\) gives \\( (r_1, r_2, ..., r_{N}) \\) values of \\( R \\) with MLEs

\\[ \hat{\mu} = \frac{1}{N \cdot T} \sum_{i = 1}^N r_i \\]

and

\\[ \hat{\sigma}^2 = \frac{1}{N \cdot T} \sum_{i = 1}^N (r_i - \hat{\mu} T)^2 \\]

to inform our governance-determined value for \\( k \\).


### Concrete Numbers


## Considerations

The analysis above is overly simplistic since:

1. It assumes all traders enter and exit positions at the same time

2. It only examines value at risk to the system on an individual market-by-market basis

3. It assumes GBM for the underlying feeds.

While useful, it is not entirely accurate. Further risk work should address each of these concerns:

1: We should think about how differing position entry prices might skew our risk estimates, and whether having funding payments incentivize *only* open interest imbalance is the optimal approach. Remember, we assumed each trader builds their position at the same time \\( 0 \\), which is unrealistic to say the least. This lead to an imbalance PnL dependent on only one entry price \\( P(0) \\) versus some form of an average. Would incorporating a more realistic model of trader behavior change things significantly given our goal is to provide suggestions for \\( k \\)?

2: We should really examine the "portfolio" of markets we're offering and the total value at risk to the system caused by the *sum of imbalances* on each individual market

\\[ 1 - \alpha = \mathbb{P}\bigg[ \sum_{i=1}^{N} {\mathrm{OI}\_{imb}}\_{i} (0) \cdot d^{-m}\_{i} \cdot \bigg( e^{\mu_i m T + \sigma_i \cdot W\_{m T}}  - 1 \bigg) \leq \mathrm{VaR}_{\alpha} (m) \bigg] \\]

where \\( (\mu_i, \sigma_i, d_i) \\) are the relevant parameters for market \\( i \\) assuming \\( N \\) total markets offered by the protocol.

3: Geometric Brownian motion, while easier to handle from a theoretical perspective, is [notoriously terrible](https://www.sciencedirect.com/science/article/abs/pii/S016920700900096X) in practice for quant finance. Most price time series exhibit fat tailed behavior, particularly within crypto. Assuming prices follow a [log-stable process](https://www.jstor.org/stable/2350970) is a more flexible approach to generalize the analysis above while accommodating for fat tails.

For example, we could assume \\( P \\) is driven by a stochastic process \\( L_t \\)

\\[ P(t) = P(0) e^{\mu t + \sigma L_t} \\]

having [Levy stable](https://en.wikipedia.org/wiki/Stable_distribution) increments, \\( L_{t+\tau} - L_{t} \sim S(a, b, 0, (\frac{\tau}{a})^{\frac{1}{a}}) \\), where \\( a \\) here is the stability parameter, \\( b \\) is the skewness parameter, and \\( c = (\frac{\tau}{a})^{\frac{1}{a}} \\) is the scale parameter. This reduces to GBM when \\( a = 2 \\).

The Levy stable CDF is not necessarily expressible analytically and estimation of parameters \\( (a, b, \mu, \sigma) \\) no longer reduces to sample mean and variance, as with GBM. However, there are easy to use [packages](https://cpb-us-w2.wpmucdn.com/sites.coecis.cornell.edu/dist/9/287/files/2019/08/Nolan-9-Nolan_Financial-Modeling-w-heavy-tailed-stable-2.pdf) to help numerically. Particularly important,

\\[ \mathrm{VaR}\_{\alpha} (m) = \mathrm{OI}\_{imb}(0) \cdot d^{-m} \cdot \bigg[ e^{\mu m T + \sigma (\frac{m T}{a})^{\frac{1}{a}} \cdot {F}^{-1}(1-\alpha)} - 1 \bigg] \\]

where \\( F^{-1} \\) is the inverse CDF for the standard Levy stable \\( S(a, b, 0, 1) \\).


## Acknowledgments

[Daniel Wasserman](https://github.com/dwasse) for pushing to directly relate funding with risk.
