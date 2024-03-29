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

- Do we have to worry about [parasitic funding](note-6#parasitic-capital)?


## Context

While contemplating ways to offer pools of capital yield while supporting the system, a question came up with the current implementation of [funding payments](note-1):

*Given an imbalance in open interest, can a large user come in and take positions on both the long and short side at the same time, in order to siphon off funding to themselves without price risk?*

Going through the example below in detail shows the current implementation of funding in fact *does* expose the parasitic user to price risk, as funding increases the user's position size on the side with less aggregate open interest. So we are not vulnerable to this type of attack.

However, the example shows that if we had taken the traditional approach to funding where only users' collateral amounts are increased/decreased, but position sizes remain intact, we would be vulnerable to this type of parasitic behavior.

### Background

The simple but illustrative example of the parasitic funding position is as follows.

Assume there are two users. The first goes long with position size \\( n \\). The second goes *both* long and short with size \\( N \\) on each side. The second user chooses size \\( N \gg n \\), to try to siphon off funding payments that would have otherwise been used as incentive for a true short.

Imbalance in open interest (OI) is then initially

\\[ \mathrm{OI}\_{imb} (0) = n \\]

at \\( t=0 \\), since \\( \mathrm{OI}\_{l} (0) = N+n \\) and \\( \mathrm{OI}\_{s} (0) = N \\).

When the next funding period passes at \\( t=1 \\), the long side transfers \\( k n \\) in open interest to the short side. The imbalance reduces to

\\[ \mathrm{OI}\_{imb} (1) = n \cdot (1-2k) \\]

with aggregate open interest values, \\( \mathrm{OI}\_{l} (1) = N+n - kn \\) and \\( \mathrm{OI}\_{s} (1) = N + kn \\), for each side. Each user pays a pro-rata share of funding from their stakes in the long side of the market.

User 1's long position size becomes

\\[ \mathrm{OI}\_{l} \|_{1} (1) = \frac{n}{N+n} \cdot (N+n-kn) \\]

User 2's long and short position sizes become

$$\begin{eqnarray}
\mathrm{OI}_{l} |_{2} (1) &=& \frac{N}{N+n} \cdot (N+n-kn) \\
\mathrm{OI}_{s} |_{2} (1) &=& N + kn
\end{eqnarray}$$

so that user 2 has total OI on the market of \\( 2N + kn \cdot \frac{n}{N+n} \\).

Assume after one funding period, the price feed has changed by \\( r \\) percent: \\( P(1) = P(0) \cdot (1 + r) \\).

## Approach to Funding

Usually, funding payments are credited/debited as PnL to/from a user's position *without* changing the size of the position -- the number of "contracts" they hold. Meaning collateral changes, but OI remains the same.

For simplicity in the math and the smart contract implementation, we chose to also alter users' position sizes on funding. This allowed us to effectively treat open interest as our "pooled" quantity for [bookkeeping in market contracts](note-5) -- we no longer would need to loop through all positions and update their associated collateral amounts on funding.

The downside to our approach is users will gain or lose exposure over time due to funding. In working through the parasitic funding attack, it's clear this is actually a feature and not a bug. If we don't change position size given the way we use funding to incentivize OI balance vs traditional price convergence, we become susceptible to parasitic funding attacks.

### OI Approach

Working through the example above with our current approach, the value (collateral + PnL) of user 1's long position after funding is

\\[ \mathrm{V} \|_{1} (1) = \frac{n}{N+n} \cdot (N+n-kn) \cdot (1 + r) \\]

with PnL

\\[ \mathrm{PnL} \|_{1} (1) = n \cdot (1 - \frac{kn}{N+n}) \cdot r - kn \cdot \frac{n}{N+n} \\]

having assumed 1x leverage for simplicity. The combined value of user 2's positions is

$$\begin{eqnarray}
\mathrm{V} |_{2} (1) &=& \frac{N}{N+n} \cdot (N+n-kn) \cdot (1 + r) + (N + kn) \cdot (1-r) \\
&=& (N-kn \cdot \frac{N}{N+n}) \cdot (1 + r) + (N + kn) \cdot (1-r) \\
&=& 2N + kn \frac{n}{N+n} - kn \cdot \frac{2N + n}{N+n} \cdot r
\end{eqnarray}$$

They have PnL

\\[ \mathrm{PnL} \|_{2} (1) = kn \frac{n}{N+n} - kn \cdot \frac{2N + n}{N+n} \cdot r \\]

which still has exposure on the short side to price fluctuations through \\( r \\). Profits for the parasitic funding position are therefore *not* risk free and require the user to move in and out of the market. They have exposure to price, given the parasite's short position size *increases* after funding occurs, increasing their exposure to the short leg of the position.


### Collateral Approach

If we take the usual approach to funding, then we run into the parasitic funding position. This is the approach taken in the original calculation [here](note-6#parasitic-capital). To see why, assume funding is instead taken from each user's PnL without affecting the size of their positions.

Open interest for each position would remain constant through funding

\\[ \mathrm{OI}\_{l} \|_{1} (1) = n \\]

\\[ \mathrm{OI}\_{l} \|_{2} (1) = N \\]

\\[ \mathrm{OI}\_{s} \|_{2} (1) = N \\]

and only collateral amounts would change

\\[ \mathrm{N}\_{l} \|_{1} (1) = \frac{n}{N+n} \cdot (N+n-kn)  \\]

\\[ \mathrm{N}\_{l} \|_{2} (1) = \frac{N}{N+n} \cdot (N+n-kn)  \\]

\\[ \mathrm{N}\_{s} \|_{2} (1) = N + kn  \\]

Value (collateral + PnL) of user 1's position would be

\\[ \mathrm{V} \|_{1} (1) = n \cdot (1+r) - kn \frac{n}{N+n} \\]

with PnL

\\[ \mathrm{PnL} \|_{1} (1) =  nr - kn \frac{n}{N+n} \\]

User 2's combination of positions, on the other hand, would have total value

$$\begin{eqnarray}
\mathrm{V} |_{2} (1) &=& \bigg[\frac{N}{N+n} \cdot (N+n-kn) + Nr \bigg] + \bigg[N + kn - Nr\bigg] \\
&=& 2N + kn \frac{n}{N+n}
\end{eqnarray}$$

resulting in a risk free profit

\\[ \mathrm{PnL} \|_{2} (1) = kn \frac{n}{N+n} \\]

without exposure to price fluctuations. Applying funding to *open interest* instead of collateral amounts then saves us from this parasitic attack.


## Concrete Numbers

Assume \\( n = 1 \\) OVL, \\( N = 99 \\) OVL and that the feed jumps 20% such that \\( r = 0.20 \\). Take the funding rate to be \\( k = 0.0025 \\).

Use the example above, where the first user enters a long and the second user enters both a long and a short.

### OI Approach

In taking the OI approach, user 1's long open interest after one funding period is \\( \mathrm{OI}\_{l} \|_{1} (1) = n - kn \cdot \frac{n}{N+n} = 0.999975 \\) OVL. They pay 1% of the total funding payment for the period.

User 2's long open interest after one funding period is \\( \mathrm{OI}\_{l} \|\_{2} (1) = N - kn \cdot \frac{N}{N+n} = 98.997525 \\) OVL. Their short open interest after one funding period is \\( \mathrm{OI}\_{s} \|\_{2} (1) = N + kn = 99.0025 \\) OVL. They pay 99% of the total funding payment, effectively shifting it to their position size on the short side.

PnL for the first user after the 20% jump in price is

\\[ \mathrm{PnL} \|_{1} (1) = 0.999975 \cdot (1+0.20) - 1 = 0.19997 \; \mathrm{OVL} \\]

PnL for the second user, however, on the parasitic funding position is

\\[ \mathrm{PnL} \|_{2} (1) = 98.997525 \cdot (1 + 0.20) + 99.0025 \cdot (1 - 0.20) - 198 = -0.00097 \; \mathrm{OVL} \\]

on a funding payment opportunity of \\( 0.0025 \\) OVL. What was assumed to be a sure gain of +0.0025 OVL, actually turned into a loss of -0.00097 OVL. Even a 1% gain in the feed (\\( r = 0.01 \\)) would result in a loss of -2.475e-05 OVL for user 2.

### Collateral Approach

Contrast with the traditional collateral approach but applied to our system. After one funding period, user 1 would pay 0.000025 from their collateral, still 1% of the total funding payment.

Their PnL would change to

\\[ \mathrm{PnL} \|_{1} (1) = 1.0 \cdot (1+0.20) - 1 - 0.000025 = 0.199975 \; \mathrm{OVL} \\]

slightly higher than in the OI approach. User 2, however, makes risk free profit. They pay 0.002475 OVL in funding for their long but receive 0.0025 OVL in funding for their short, a net gain of 2.5e-05 OVL. This is simply user 1's portion of the funding payment.

User 2's PnL would change to

\\[ \mathrm{PnL} \|_{2} (1) = 99 \cdot (1 + 0.20) + 99 \cdot (1 - 0.20) - 0.002475 + 0.0025 - 198 = 0.000025 \; \mathrm{OVL} \\]

yielding risk free profit.


## Considerations

Users have to be careful in adjusting to this unusual approach we're taking to funding. Your exposure to the position, along with collateral amounts, increases/decreases with funding payments through our aggregate open interest quantities.

Users can see this through our expression for the value of their position

\\[ \mathrm{V} (t) = \mathrm{OI} (t) - D \pm \mathrm{OI} (t) \cdot \bigg(\frac{P(t)}{P(0)} - 1 \bigg) \\]

where \\( \mathrm{N}(t) \equiv \mathrm{OI} (t) - D \\) is the collateral we associate with the position. \\( D = N \cdot (L - 1) \\) is their debt to the protocol for taking out leverage \\( L \\) on their initially deposited collateral \\( N \\).

As funding is paid, \\( \mathrm{N}(t) \\) decreases alongside \\( \mathrm{OI} (t) \\) (\\(D\\) is static).


### Fees Paid

How does this compare in terms of funding fees paid by the user? User 1's PnL after one funding period shows the difference.

With the OI approach, their PnL is

$$\begin{eqnarray}
\mathrm{PnL} |_{1} (1) &=& n \cdot (1 - \frac{kn}{N+n}) \cdot r - kn \cdot \frac{n}{N+n} \\
&=& n \cdot r - kn \cdot \frac{n}{N+n} \cdot (1 + r)
\end{eqnarray}$$

but with the collateral approach

\\[ \mathrm{PnL} \|_{1} (1) = n \cdot r - kn \cdot \frac{n}{N+n} \\]

where \\( k \cdot \frac{n}{N+n} \\) is the funding rate for this period. The adjustment in position size to pay funding (OI approach) effectively increases their funding cost by

\\[ kn \cdot \frac{n}{N+n} \cdot r \\]

to maintain the position. For the numbers above, this amounts to a difference of 0.000005 OVL or a 20% higher funding rate vs the base they would have paid for their pro-rata share at 1% of 0.25%, given price spiked 20%.


### Effective Leverage

The difference in funding has an effect on the current leverage a position has. We'll generalize a bit here with some formalism. Take the effective leverage of a position as its notional (value + debt) divided by its value such that

\\[ \mathrm{EL}(t) \equiv 1 + \frac{D}{\mathrm{V}(t)} \\]

and define the funding *rates* paid by the longs for this period and received by the shorts as

$$\begin{eqnarray}
f_l(t) &\equiv& k \cdot \frac{\mathrm{OI}_{imb} (t)}{\mathrm{OI}_{l}(t)} \\
f_s(t) &\equiv& k \cdot \frac{\mathrm{OI}_{imb} (t)}{\mathrm{OI}_{s}(t)}
\end{eqnarray}$$

Open interest associated with user 1's position after one funding period in the OI approach becomes

\\[ \mathrm{OI}\_{l} \|\_{1} (1) = \mathrm{OI}\_{l} \|\_{1} (0) \cdot \bigg [ 1 - f_l(0) \bigg] \\]

such that the value of their position is

$$\begin{eqnarray}
\mathrm{V}_{l} |_{1} (1) &=& \mathrm{OI}_{l} |_{1} (1) \cdot (1 + r) - D \\
&=& \mathrm{OI}_{l} |_{1} (0) \cdot \bigg[ 1 - f_l(0) \bigg] \cdot (1 + r) - D \\
&=& \mathrm{N}|_{1} (0) + \mathrm{OI}_{l} |_{1} (0) \cdot \bigg[r - f_l(0) \cdot (1 + r) \bigg]
\end{eqnarray}$$

Compare this with the collateral only approach to funding for the value of the position \\( \mathrm{N}\|\_{1} (0) + \mathrm{OI}_{l} \|\_{1} (0) \cdot [r - f_l (0) ] \\), and we see the OI approach scales the rate of return further than paying from collateral only. The difference between the two approaches is the cost term \\( -\mathrm{OI}\_{l} \|\_{1} (0) \cdot f_l(0) \cdot r \\).

The associated effect on leverage is clear. For positive \\( r > 0 \\), the paying long will have a smaller position value, and thus higher effective leverage than in the traditional collateral approach to funding. Still, the position will be less levered than the prior period as long as \\( f_l(0) < \frac{r}{1+r} \\).

Conversely, for negative \\( r < 0 \\), the paying long will have a larger position value and thus smaller effective leverage. The additional term then buffers moves in \\( r \\) for the postion value of the paying long.
