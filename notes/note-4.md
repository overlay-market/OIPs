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

Return to the functional form of our [funding payments](note-1) \\( \mathrm{FP}_n \\)

\\[ \mathrm{FP}\_n = k \cdot \mathrm{OI}\_{imb}(t_n) \\]

where \\( {\mathrm{OI}\_{imb}}_n = {\mathrm{OI}_l}_n - {\mathrm{OI}_s}_n \\) is the open interest imbalance between the long and short side on a market at time \\( t_n \\).

We need some guidance on what to set the value of \\( k \\) as for every update period. \\( k \\) dictates the rate at which funds flow from longs to shorts or shorts to longs to rebalance the system and draw down the risk associated with an imbalanced book. Thus, \\( k \\) should be related to the risk the underlying feed adds to the system and inherently passive OVL holders through the currency supply.

To start, consider the case where \\( \mathrm{OI}_{imb} > 0 \\) so longs outweigh shorts. For simplicity, assume no more positions are built or unwound on either side such that the total open interest remains a constant: \\( \mathrm{OI}_l + \mathrm{OI}_s = \mathrm{const} \\). The latter assumption will skew our risk estimates, but likely to the more conservative side given funding incentives should trend towards a more balanced book over time.


## Risk-Based Approach to Balancing Markets

### Imbalance Over Time

What does the evolution of the imbalance look like over time  when we factor in funding payments? Given open interest on a market for the long side of \\( \mathrm{OI}_l \\) and short side of \\( \mathrm{OI}_s \\), take the imbalance on the market at time \\( t_n \\) to be \\( {\mathrm{OI}\_{imb}}\_n = {\mathrm{OI}_l}_n - {\mathrm{OI}_s}_n > 0 \\). In terms of the prior period \\( t\_{n-1} \\), open interest on the long side after paying the funding payment will be

\\[ {\mathrm{OI}\_{l}}_n = {\mathrm{OI}\_{l}}\_{n-1} - \mathrm{FP}\_{n-1} \\]

and short side after receiving funding

\\[ {\mathrm{OI}\_{s}}_n = {\mathrm{OI}\_{s}}\_{n-1} + \mathrm{FP}\_{n-1} \\]

Subtracting the two and expanding \\( \mathrm{FP}_{n-1} \\) gives the time evolution of the imbalance from block \\( n-1 \\) to block \\( n \\)

\\[ {\mathrm{OI}\_{imb}}_n = {\mathrm{OI}\_{imb}}\_{n-1} \cdot ( 1 - 2k ) \\]

Rinse and repeat \\( n \\) times to get the time evolution as a function of the value of the open interest imbalance when traders initially enter their positions

\\[ {\mathrm{OI}\_{imb}}_n = {\mathrm{OI}\_{imb}}\_{0} \cdot ( 1 - 2k )^n \\]

where \\( k \in [0, \frac{1}{2}] \\).


### Risk to the System

One can view the risk to the system at time \\( t_0 \\) due to the long imbalance created on this market as the expected PnL the system would need to pay out to a long position with notional \\( {\mathrm{OI}_{imb}}_0 > 0 \\) at some time in the future \\( t_n \\):

\\[ {\mathrm{PnL}\_{imb}}_n = {\mathrm{OI}\_{imb}}\_{n} \cdot \bigg[ \frac{P_n}{P_0} - 1 \bigg] \\]

where \\( P_n = P(t_n) \\) is the future value of the underlying feed at time \\( t_n \\) and \\( P_0 \\) the value at the current time \\( t_0 \\). Our results will also be the same when \\( {\mathrm{OI}_{imb}}_0 < 0 \\).

Take \\( P : \Omega \to \mathbb{R} \\) to be a random variable on the probability space \\( (\Omega, \mathcal{F}, \mathrm{P}) \\) driven by a stochastic process \\( W_t \\)

\\[ P_t = P_0 e^{\mu \cdot t + \sigma \cdot W_t} \\]

such that the feed exhibits Geometric Brownian motion (GBM) when \\( W_t \\) is a Wiener process. Assume GBM for now even though DeFi price feeds will be far more fat-tailed (we'll have to be more conservative with \\( k \\) values chosen). \\( dP_t = P_t \cdot [ (\mu + \frac{\sigma^2}{2}) \cdot dt + \sigma \cdot dW_t ] \\) and PnL at time \\( t_n \\) from this hypothetical long position reduces to

\\[ {\mathrm{PnL}\_{imb}}_n = {\mathrm{OI}\_{imb}}\_{0} \cdot ( 1 - 2k )^n \cdot \bigg[ e^{\mu \cdot n \cdot T + \sigma \cdot W\_{n \cdot T}}  - 1 \bigg] \\]

where \\( t_n - t_0 = n \cdot T \\) and \\( T \\) is the length of time between funding payments.

Our approach will be to choose a \\( k \\) that minimizes the expected value of the PnL, \\( \mathbb{E}[ {\mathrm{PnL}\_{imb}}\_n \| \mathcal{F}_{n} ] \\), for this "position" within a finite number \\( n \\) time intervals to reduce risk to the system. Taking the expected value of above

\\[ \mathbb{E}[ {\mathrm{PnL}\_{imb}}\_n \| \mathcal{F}_{n} ] = {\mathrm{OI}\_{imb}}\_{0} \cdot ( 1 - 2k )^n \cdot \bigg[ e^{\mu \cdot n \cdot T} \cdot \mathbb{E}[e^{\sigma \cdot W\_{n \cdot T}}]  - 1 \bigg] \\]

But, using \\( W_{n \cdot T} \sim \mathcal{N}(0, n \cdot T) \\) and the PDF of the [normal distribution](https://en.wikipedia.org/wiki/Normal_distribution), \\( \mathbb{E}[e^{\sigma \cdot W\_{n \cdot T}}] = (1 / \sqrt{2 \pi}) \int_{\mathbb{R}} dz \; e^{\sigma \cdot \sqrt{n \cdot T} \cdot z - z^2 / 2} = e^{\sigma^2 \cdot n \cdot T / 2} \cdot (1 / \sqrt{2 \pi}) \int_{\mathbb{R}} dz' \; e^{- z'^2 / 2} = e^{\sigma^2 \cdot n \cdot T / 2} \\), simplifying our expression for the expected value the system needs to pay out for the imbalance to

\\[ \mathbb{E}[ {\mathrm{PnL}\_{imb}}\_n \| \mathcal{F}_{n} ] = {\mathrm{OI}\_{imb}}\_{0} \cdot ( 1 - 2k )^n \cdot \bigg[ \bigg(e^{(\mu + \sigma^2 / 2) \cdot T} \bigg)^n  - 1 \bigg] \\]

Let \\( a = \frac{1}{1 - 2k} \\), where \\( a \in [1, \infty) \\):

\\[ \mathbb{E}[ {\mathrm{PnL}\_{imb}}\_n \| \mathcal{F}_{n} ] = {\mathrm{OI}\_{imb}}\_{0} \cdot a^{-n} \cdot \bigg[ \bigg(e^{(\mu + \sigma^2 / 2) \cdot T} \bigg)^n  - 1 \bigg] \\]

This reduces our task to choosing an appropriate value for \\( a \gg e^{(\mu + \sigma^2 / 2) \cdot T} \\) such that the expected value of the imbalance profit significantly decays over time as more blocks go by. Take

\\[ a = b \cdot e^{(\mu + \sigma^2 / 2) \cdot T} \\]

where \\( b \in (1, \infty) \\). As \\( n \to \infty \\),

\\[ \lim_{n\to\infty} \mathbb{E}[ {\mathrm{PnL}\_{imb}}\_n \| \mathcal{F}_{n} ] = {\mathrm{OI}\_{imb}}\_{0} \cdot \bigg( \frac{e^{(\mu + \sigma^2 / 2) \cdot T}}{a} \bigg)^n = \frac{ {\mathrm{OI}\_{imb}}\_0 }{b^n} = 0 \\]

producing the behavior we want when \\( b > 1 \\). In terms of \\( k \\)

\\[ k = \frac{1}{2} \cdot \bigg[ 1 - \frac{1}{b \cdot e^{(\mu + \sigma^2 / 2) \cdot T}} \bigg] \\]

Notice, this relates our chosen value for \\( k \\) to properties of the underlying feed (i.e. drift and volatility).


### Value at Risk

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

The former condition will likely be more restrictive as \\( \alpha \to 0^{+} \\).


### Determining \\( \mu \\) and \\( \sigma^2 \\)

We'll use maximum likelihood estimation (MLE) from on-chain samples to find our \\( \mu \\) and \\( \sigma^2 \\) values. At launch, we should have these simply inform our chosen \\( k \\) values over rolling time periods versus automating completely, and allow governance to tweak funding rates given existing risk conditions. So more as guidelines for funding rates in the current time period, given assumptions of GBM won't be accurate over longer time horizons.

Assume \\( T \\) is the `periodSize` of a [sliding window TWAP oracle](note-2), such that funding is paid upon every price update of an Overlay market, versus per block (results will be the same). Let

\\[ R_i = \ln \bigg( \frac{P_i}{P_{i-1}} \bigg) = \mu \cdot T + \sigma \cdot [ W_{i \cdot T} - W_{(i-1) \cdot T} ] \sim \mathcal{N}(\mu \cdot T, \sigma^2 \cdot T) \\]

Sampling \\( N+1 \\) of these windows over a length of time \\( (N + 1) \cdot T \\) for \\( (r_1, r_2, ..., r_{N}) \\) values of \\( R \\) gives MLEs

\\[ \hat{\mu} = \frac{1}{N \cdot T} \cdot \sum_{i = 1}^N r_i \\]

and

\\[ \hat{\sigma}^2 = \frac{1}{N \cdot T} \cdot \sum_{i = 1}^N (r_i - \hat{\mu} \cdot T)^2 \\]

to inform our governance-determined value for \\( k \\).

With our proposed feeds at launch likely coming from an implementation of Keep3r Network's [Keep3rV1Oracle](https://github.com/keep3r-network/keep3r.network/blob/master/contracts/jobs/Keep3rV1Oracle.sol#L685) with SushiSwap TWAPs as the underlying, we should be able to calculate these rolling estimations [on-chain](https://github.com/keep3r-network/keep3r.network/blob/master/contracts/Keep3rV1Volatility.sol#L268).


### Concrete Numbers
