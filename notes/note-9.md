---
note: 9
oip-num: 1
title: EV with Caps & Tails
status: WIP
author: Bob
discussions-to: oip-1
created: 2022-07-22
updated: N/A
---

Issue to address:

- Solve the integral

\\[ \frac{1}{2\pi} \int_{-\infty}^{z_{max}} dz \int_{-\infty}^{\infty} ds \; e^{(p-is)z - \| s \|^{a}} \\]

where \\( p > 0 \\) and \\( a \in (0, 2] \\). Note that for \\( a = 2 \\) and \\( z_{max} \to \infty \\), the integral reduces to

\\[ e^{p^2} \\]

since the integral in this limit is the moment generating function (MGF) of a [normal distribution](https://en.wikipedia.org/wiki/Normal_distribution) with mean 0 and variance 2.

### Possible approach

I believe solving the general expression likely requires extending integrand \\( ds \\) into the complex plane (at least this was my approach). Poles appear to be \\( s = \pm ip \\), but I'm getting sign errors with the residue theorem. I haven't tried to do this out super rigorously yet though.

## Context

Assume a log-stable process drives the underlying price feed users are trading on. This lets us model with fat tails. Then the price at any given time in the future is given by

\\[ P(t) = P(0) e^{\mu t + \sigma L_t} \\]

where \\( L_{t} \\) is a Levy stable stochastic process with increments that follow a [stable distribution](https://en.wikipedia.org/wiki/Stable_distribution) \\( L_{t+\tau} - L_{t} \sim S(a, b, 0, (\frac{\tau}{a})^{\frac{1}{a}}) \\). \\( a \\) is the stable distribution stability parameter, \\( b \\) is the skewness parameter, and \\( c = (\frac{\tau}{a})^{\frac{1}{a}} \\) is the scale parameter, for time increments of length \\( \tau \\). \\( \mu \\) is a drift parameter and \\( \sigma \\) is a volatility parameter.

This reduces to [Geometric Brownian motion](https://en.wikipedia.org/wiki/Geometric_Brownian_motion) for \\( a = 2 \\), where the increments become log-normal.

Using log-stable, we want to find the expected value of losses the protocol takes on given an imbalance in longs vs shorts on a market. Recall, this is given per market by an expression proportional to \\( \frac{P(t)}{P(0)} - 1 \\). This means that, if we use our fat tail approach, the expected value of profits to be paid out at any time \\( \tau \\) in the future given an initial imbalance is proportional to

\\[ \mathbb{E}[ \mathrm{PnL}\_{imb}(\tau) ] \propto \mathbb{E}[ e^{\mu \tau + \sigma (\frac{\tau}{a})^{1/a} Z } - 1 ]  \\]

where \\( Z \sim S(a, b, 0, 1) \\) is a standard stable distribution. I've used the scaling property of the stable distribution \\( Y = c Z \\), for \\( Z \sim S(a, b, 0, 1) \\) and \\( Y \sim S(a, b, 0, c) \\).

Using properties of the expectation value, the real expression we want to solve for is

\\[ \mathbb{E}[e^{pZ}] \\]

in \\( e^{\mu \tau} \cdot \mathbb{E}[e^{pZ}] - 1 \\), where we define \\( p \equiv \sigma (\frac{\tau}{a})^{1/a} \\). This expectation value is simply the moment generating function (MGF) of the standard stable distribution with stability \\( a \\) and skewness \\( b \\). However, it is *undefined* for anything except \\( a = 2 \\), and equal to \\( e^{p^2} \\) when \\( a \\) does equal 2 -- related to the fact that [moments of the stable distribution will be infinite](https://cpb-us-w2.wpmucdn.com/sites.coecis.cornell.edu/dist/9/287/files/2019/08/Nolan-9-Nolan_Financial-Modeling-w-heavy-tailed-stable-2.pdf) for \\( p \geq a \\) when \\( a < 2 \\).

This is scary from an imbalance PnL perspective because we're now dealing with infinities. We resolve this through capping the payoffs offered to traders, which effectively [cuts off the tails](note-7). So instead of above, our imbalance PnL is proportional to

\\[ \mathrm{PnL}\_{imb}(\tau) \propto \min\bigg(\bigg[ \frac{P(\tau)}{P(0)} - 1 \bigg], C_p \bigg) \\]

where \\( C_p \\) is our chosen payoff cap (e.g. 5x), which is a constant. We now have an expression we can work with to find the expected value of the imbalance PnL because we've [removed the infinities in the moments of the payout caused by the tails](https://www.sciencedirect.com/science/article/abs/pii/S016920700900096X).

Define the payoff function

\\[ g(z) \equiv e^{\mu \tau + \sigma (\frac{\tau}{a})^{1/a} z} - 1 \\]

The expected value of the imbalance PnL for the same standard stable distribution \\( Z \\) with stability \\( a \\) and skewness \\( b \\) above is now proportional to

\\[ \mathbb{E}[\mathrm{PnL}\_{imb}(\tau)] \propto \mathbb{E}[\min (g(Z), C_p)] = \int_{-\infty}^{\infty} dz \; \min (g(z), C_p) \cdot f(z) \\]

where \\( f(z) \\) is the PDF of \\( Z \\). The integral can be split up over two domains \\( -\infty < z < g^{-1}(C_p) \\) and \\( g^{-1}(C_p) < z < \infty \\):

\\[ \mathbb{E}[\mathrm{PnL}\_{imb}(\tau)] \propto \int_{-\infty}^{g^{-1}(C_p)} dz \; g(z) \cdot f(z) + C_p \cdot \int^{\infty}_{g^{-1}(C_p)} dz \; f(z) \\]

Notice, the extreme values of \\( g(z) \\) that result from \\( z \to \infty \\) are completely removed and replaced by a constant value \\( C_p \\), so the exponential in \\( g(z) \\) for large values of \\( z \\) will no longer cause the infinities in our expected value calculation. By definition, \\( \mathbb{P}[Z > g^{-1}(C_p)] = \int^{\infty}_{g^{-1}(C_p)} dz \; f(z) \\), which is finite and also equal to \\( 1 - F(g^{-1}(C_p)) \\). \\( F(z) \\) is the CDF of our standard stable \\( Z \\), easily computable with [`pystable`](https://github.com/overlay-market/pystable).

Let \\( z_{max} \equiv g^{-1}(C_p) \\). Plugging in \\( g(z) \\) for the first integral

\\[ \int_{-\infty}^{z_{max}} dz \; g(z) \cdot f(z) = e^{\mu \tau} \int_{-\infty}^{z_{max}} dz \; e^{p z} f(z) - F(z_{max}) \\]

Combine this with the second integral expression to get

\\[ \mathbb{E}[\mathrm{PnL}\_{imb}(\tau)] \propto e^{\mu \tau} \int_{-\infty}^{z_{max}} dz \; e^{p z} f(z) - F(z_{max}) + C_p \cdot \bigg[ 1 - F(z_{max}) \bigg] \\]

The first integral

\\[ \int_{-\infty}^{z_{max}} dz \; e^{p z} f(z) \\]

is what we still need to solve for. The PDF of the stable distribution isn't necessarily analytically expressible except for a few values of \\( a \\) and \\( b \\). However, the characteristic function (CF), \\( \phi (s) = \mathbb{E}[e^{isZ}] \\), is

\\[ \phi (s) = e^{-\| s \|^{a} (1 - i b \cdot \mathrm{sgn}(s) \Phi )} \\]

where

$$\begin{eqnarray}
  \Phi =
    \begin{cases}
      \tan(\frac{\pi a}{2}) & \quad a \neq 1 \\\\
      - \frac{2}{\pi} \ln | s | & \quad a = 1
    \end{cases}
\end{eqnarray}$$

and I've assumed the form of the CF for \\( Z \sim S(a, b, 0, 1) \\). The characteristic function is simply the Fourier transform of the PDF and therefore related by

\\[ f(z) = \frac{1}{2\pi} \int_{-\infty}^{\infty} ds \; e^{-isz} \phi (s) \\]

Our first integral becomes

\\[ \frac{1}{2\pi} \int_{-\infty}^{z_{max}} dz \int_{-\infty}^{\infty} ds \; e^{(p-is)z} \phi (s) \\]

To make things easier to start, simplify and assume zero skewness \\( b = 0 \\), so \\( \phi (s) = e^{-\|s\|^a} \\). Then, we come to the original integral we'd like to solve for

\\[ \frac{1}{2\pi} \int_{-\infty}^{z_{max}} dz \int_{-\infty}^{\infty} ds \; e^{(p-is)z - \|s\|^a} \\]


## Considerations

Figuring this integral out will also likely be important for pricing *capped* options contracts, if we ever want to offer those -- extension of Black Scholes European pricing formulas for fat tails on capped calls and puts. The price of a European capped call will be

\\[ \mathbb{E}^{\mathbb{Q}}\bigg[ \min \bigg( \max (P(\tau) - K, 0), C_p \bigg) \bigg] \\]

where \\( \mathbb{Q} \\) is the risk-neutral measure and we'll assume \\( P(\tau) \\) is driven by a log-stable process.
