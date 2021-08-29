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

However, the example shows that if we had taken the traditional approach to funding where only users' collateral amounts are increased/decreased, but position sizes (OI) remain intact, we would be vulnerable to this type of parasitic behavior.

### Background

Assume two traders. The first goes long with position size \\( n \\). The second goes *both* long and short with size \\( N \\). The second trader chooses size \\( N \gg n \\), to try to siphon off funding payments that would have otherwise been used as incentive for a true short.

Imbalance in open interest is then initially at \\( t=0 \\)

\\[ \mathrm{OI}\_{imb} (0) = n \\]

since \\( \mathrm{OI}\_{l} (0) = N+n \\) and \\( \mathrm{OI}\_{s} (0) = N \\).

When the next funding period passes at \\( t=1 \\), the long side transfers \\( k n \\) in open interest to the short side. The imbalance reduces to

\\[ \mathrm{OI}\_{imb} (1) = n \cdot (1-2k) \\]

with aggregates \\( \mathrm{OI}\_{l} (1) = N+n - kn \\) and \\( \mathrm{OI}\_{s} (1) = N + kn \\).

Each trader pays a pro-rata share of funding. Trader 1's long position size becomes

\\[ \mathrm{OI}\_{l} \|_{1} (1) = \frac{n}{N+n} \cdot (N+n-kn) \\]

Trader 2's long and short position sizes become

$$\begin{eqnarray}
\mathrm{OI}_{l} |_{2} (1) &=& \frac{N}{N+n} \cdot (N+n-kn) \\
\mathrm{OI}_{s} |_{2} (1) &=& N + kn
\end{eqnarray}$$

so that trader 2 has total OI on the market of \\( 2N + kn \cdot \frac{n}{N+n} \\).

Assume after one funding period, the price feed has changed by \\( r \\) percent: \\( P(1) = P(0) \cdot (1 + r) \\).

## Approach to Funding

Usually, funding payments are paid directly to a trader's collateral amount *without* changing the size of their positions (OI). Given 
