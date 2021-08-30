---
note: 9
oip-num: 1
title: On Parasitic Funding
status: WIP
author: Michael Feldman (@mikeyrf)
discussions-to: oip-1
created: 2021-08-29
updated: N/A
---

Issue to address with this note:

- Do we have to worry about the [parasitic funding trade](note-6#parasitic-capital)?


## Context

While contemplating ways to offer pools of capital yield while supporting the system, a question came up with the current implementation of [funding payments](note-1):

*Given an imbalance in open interest, can a large trader come in and take positions on both the long and short side at the same time, in order to siphon off funding to themselves without price risk?*

Going through the example below in detail shows the current implementation of funding in fact *does* expose the parasitic trader to price risk, as funding increases the trader's position size on the side with less aggregate open interest. So we are not vulnerable to this type of attack.

However, the example shows that if we had taken the traditional approach to funding where only users' collateral amounts are increased/decreased, but position sizes remain intact, we would be vulnerable to this type of parasitic behavior.

### Background

The simple but illustrative example of the parasitic funding trade is as follows.

Assume there are two traders. The first goes long with position size \\( n \\). The second goes *both* long and short each with size \\( N \\). The second trader chooses size \\( N \gg n \\), to try to siphon off funding payments that would have otherwise been used as incentive for a true short.

Imbalance in open interest (OI) is then initially

\\[ \mathrm{OI}\_{imb} (0) = n \\]

at \\( t=0 \\), since \\( \mathrm{OI}\_{l} (0) = N+n \\) and \\( \mathrm{OI}\_{s} (0) = N \\).

When the next funding period passes at \\( t=1 \\), the long side transfers \\( k n \\) in open interest to the short side. The imbalance reduces to

\\[ \mathrm{OI}\_{imb} (1) = n \cdot (1-2k) \\]

with aggregate open interest values, \\( \mathrm{OI}\_{l} (1) = N+n - kn \\) and \\( \mathrm{OI}\_{s} (1) = N + kn \\), for each side. Each trader pays a pro-rata share of funding from their stakes in the long side of the market.

Trader 1's long position size becomes

\\[ \mathrm{OI}\_{l} \|_{1} (1) = \frac{n}{N+n} \cdot (N+n-kn) \\]

Trader 2's long and short position sizes become

$$\begin{eqnarray}
\mathrm{OI}_{l} |_{2} (1) &=& \frac{N}{N+n} \cdot (N+n-kn) \\
\mathrm{OI}_{s} |_{2} (1) &=& N + kn
\end{eqnarray}$$

so that trader 2 has total OI on the market of \\( 2N + kn \cdot \frac{n}{N+n} \\).

Assume after one funding period, the price feed has changed by \\( r \\) percent: \\( P(1) = P(0) \cdot (1 + r) \\).

## Approach to Funding

Usually, funding payments are credited/debited as PnL to/from a trader's position *without* changing the size of the position -- the number of "contracts" they hold. Meaning collateral changes, but OI remains the same.

For simplicity in the math and the smart contract implementation, we chose to instead also alter traders' position sizes on funding. This allowed us to effectively treat open interest as our "pooled" quantity for [bookkeeping in market contracts](note-5) -- we no longer would need to loop through all positions and update their associated collateral amounts on funding.

The downside to our approach is traders will gain or lose exposure over time due to funding. In working through the parasitic funding attack, it's clear this is actually a feature and not a bug. If we don't change position size on funding given the way we use funding to incentivize OI balance vs traditional price convergence, we become susceptible to parasitic funding attacks.

### OI Approach

Working through the example above with our current approach, the value (collateral + PnL) of trader 1's long position after funding is

\\[ \mathrm{V} \|_{1} (1) = \frac{n}{N+n} \cdot (N+n-kn) \cdot (1 + r) \\]

with PnL

\\[ \mathrm{PnL} \|_{1} (1) = n \cdot (1 - \frac{kn}{N+n}) \cdot r - kn \cdot \frac{n}{N+n} \\]

assuming 1x leverage for simplicity. The combined value of trader 2's positions is

$$\begin{eqnarray}
\mathrm{V} |_{2} (1) &=& \frac{N}{N+n} \cdot (N+n-kn) \cdot (1 + r) + (N + kn) \cdot (1-r) \\
&=& (N-kn \cdot \frac{N}{N+n}) \cdot (1 + r) + (N + kn) \cdot (1-r) \\
&=& 2N + kn \frac{n}{N+n} - kn \cdot \frac{2N + n}{N+n} \cdot r
\end{eqnarray}$$

They have PnL

\\[ \mathrm{PnL} \|_{2} (1) = kn \frac{n}{N+n} - kn \cdot \frac{2N + n}{N+n} \cdot r \\]

which still has significant exposure on the short side to price fluctuations, \\( r \\). Profits for the parasitic funding trade are therefore not risk free and require the trader to move in and out of the market. They have exposure to price, given the parasite's short position size *increases* after funding occurs, increasing their exposure to the short leg of the trade.


### Collateral Approach

If we take the usual approach to funding, then we run into the parasitic funding trade. This is the approach taken in the original calculation [here](note-6#parasitic-capital). To see why, assume funding is instead taken from each trader's PnL without affecting the size of their positions.

Open interest for each position would remain constant through funding

\\[ \mathrm{OI}\_{l} \|_{1} (1) = n \\]

\\[ \mathrm{OI}\_{l} \|_{2} (1) = N \\]

\\[ \mathrm{OI}\_{s} \|_{2} (1) = N \\]

and only collateral amounts would change

\\[ \mathrm{N}\_{l} \|_{1} (1) = \frac{n}{N+n} \cdot (N+n-kn)  \\]

\\[ \mathrm{N}\_{l} \|_{2} (1) = \frac{N}{N+n} \cdot (N+n-kn)  \\]

\\[ \mathrm{N}\_{s} \|_{2} (1) = N + kn  \\]

Value (collateral + PnL) of trader 1's position would be

\\[ \mathrm{V} \|_{1} (1) = n \cdot (1+r) - kn \frac{n}{N+n} \\]

with PnL

\\[ \mathrm{PnL} \|_{1} (1) =  nr - kn \frac{n}{N+n} \\]

Trader 2's combination of positions, on the other hand, would have total value

$$\begin{eqnarray}
\mathrm{V} |_{2} (1) &=& \bigg[\frac{N}{N+n} \cdot (N+n-kn) + Nr \bigg] + \bigg[N + kn - Nr\bigg] \\
&=& 2N + kn \frac{n}{N+n}
\end{eqnarray}$$

resulting in a risk free profit

\\[ \mathrm{PnL} \|_{2} (1) = kn \frac{n}{N+n} \\]

without exposure to price fluctuations. Applying funding to *open interest* instead of collateral amounts saves us from this parasitic attack.


## Concrete Numbers

<!-- Besides example of losing money, also show diff in funding rate effects in OI vs collateral approach -->

## Considerations
