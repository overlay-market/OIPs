import pystable
import pandas as pd
import numpy as np

from scipy import integrate


FILENAME = "ethusd_01012020_08232021"
FILEPATH = f"csv/{FILENAME}.csv"  # datafile
T = 4  # 1m candle size on datafile
V = 40  # 10 m shorter TWAP
CP = 4  # 5x payoff cap

# uncertainties
ALPHAS = np.array([0.01, 0.025, 0.05, 0.075, 0.1])
# target OI threshold beyond which scalp trade is negative EV
Q0S = np.array([0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1])


def gaussian():
    return pystable.create(alpha=2.0, beta=0.0, mu=0.0,
                           sigma=1.0, parameterization=1)


def rescale(dist: pystable.STABLE_DIST, t: float) -> pystable.STABLE_DIST:
    mu = dist.contents.mu_1 * t
    if t > 1:
        sigma = dist.contents.sigma * \
            (t/dist.contents.alpha)**(1/dist.contents.alpha)
    else:
        sigma = dist.contents.sigma * \
            ((1/t)/dist.contents.alpha)**(-1/dist.contents.alpha)

    return pystable.create(
        alpha=dist.contents.alpha,
        beta=dist.contents.beta,
        mu=mu,
        sigma=sigma,
        parameterization=1
    )


def delta(a: float, b: float, mu: float,
          sig: float, v: float, alphas: np.ndarray) -> np.ndarray:
    d = pystable.create(alpha=a, beta=b, mu=0.0, sigma=1.0, parameterization=1)
    qs = pystable.q(d, list(1-alphas), len(alphas))
    qs = np.array(qs)
    return (mu * v + sig * ((v/a)**(1/a)) * qs) / 2.0


def y(dist: pystable.STABLE_DIST,
      delta: float, v: float) -> pystable.STABLE_DIST:
    mu = dist.contents.mu_1*v - 2*delta
    sigma = dist.contents.sigma * \
        (v/dist.contents.alpha)**(1/dist.contents.alpha)
    return pystable.create(
        alpha=dist.contents.alpha,
        beta=dist.contents.beta,
        mu=mu,
        sigma=sigma,
        parameterization=1
    )


def main():
    df = pd.read_csv(FILEPATH)
    p = df['c'].to_numpy() if 'c' in df else df['twap']
    log_close = [np.log(p[i]/p[i-1]) for i in range(1, len(p))]

    dst = gaussian()  # use gaussian as init dist to fit from
    pystable.fit(dst, log_close, len(log_close))
    print(f"alpha: {dst.contents.alpha}, beta: {dst.contents.beta}, mu: {dst.contents.mu_1}, sigma: {dst.contents.sigma}")
    dst = rescale(dst, 1/T)

    # calc deltas
    deltas = delta(dst.contents.alpha, dst.contents.beta,
                   dst.contents.mu_1, dst.contents.sigma, V, ALPHAS)
    df_deltas = pd.DataFrame(data=[ALPHAS, deltas]).T
    df_deltas.columns = ['alpha', 'delta']
    print('deltas:', df_deltas)
    df_deltas.to_csv(f"csv/metrics/{FILENAME}-deltas.csv", index=False)

    # calc lambda (mkt impact)
    g_inv = np.log(1+CP)
    ls = []
    for dlt in deltas:
        dst_y = y(dst, dlt, V)
        def integrand(y): return pystable.pdf(dst_y, [y], 1)[0] * np.exp(y)
        numerator, _ = integrate.quad(integrand, 0, g_inv)
        denominator = 1-pystable.cdf(dst_y, [0], 1)[0] \
            - (1+CP)*(1-pystable.cdf(dst_y, [g_inv], 1)[0])
        ls.append([np.log(numerator/denominator)/q for q in Q0S])

    df_ls = pd.DataFrame(
        data=ls,
        columns=[f"q0={q0}" for q0 in Q0S],
        index=[f"alpha={alpha}" for alpha in ALPHAS]
    )
    print('lambdas:', df_ls)
    df_ls.to_csv(f"csv/metrics/{FILENAME}-lambdas.csv")


if __name__ == '__main__':
    main()
