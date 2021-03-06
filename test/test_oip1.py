import typing as tp
from util import *
import numpy as np
import unittest
import pytest




amt_OVL = 100
amt_ETH = 1

class TestOIP1(unittest.TestCase):

    def test_util_fcns(self):
        #ETH is expensive rwt OVL: if ETH = $2000, then OVL = $20
        P0 = 100
        assert toETH(amt_OVL, P0) == 1
        assert fromETH(amt_ETH, P0) == P0
        assert fromETH(fromOVL(amt_OVL, P0), P0) == amt_OVL
        assert fromOVL(fromETH(amt_OVL, P0), P0) == amt_OVL

        assert np.isclose(px_from_ret(P0, 50), 150)
        assert np.isclose(px_from_ret(P0, 200), 300)
        assert np.isclose(px_from_ret(P0, -50), 50)

        assert pnl(100, 50) == 150
        assert pnl(100, -50) == 50


    def test_price(self):
        #ETH is expensive rwt OVL: if ETH = $2000, then OVL = $20
        P0 = 100
        #we have 100 OVL, we buy ETH, we expect to have 1 ETH
        amt_ETH = toETH(amt_OVL, P0)
        self.assertEqual(amt_ETH, 1)

        #OVL is expensive rwt to ETH: if ETH = $2000, then OVL = $200000
        P0 = .01
        #we have 100 OVL, we buy ETH, we expect to have 10000 ETH
        amt_ETH = toETH(amt_OVL, P0)
        self.assertEqual(amt_ETH, 10000)

    def test_cost(self):
        '''
        The cost in ETH terms to enter the 1x long ETH-OVL trade on Overlay is \\[ C = \frac{n}{P_0} \\]
        '''
        #ETH is expensive rwt OVL: if ETH = $2000, then OVL = $20
        P0 = 100
        #we have 1 ETH, we buy OVL, we expect to have 100 OVL
        amt_OVL = toOVL(amt_ETH, P0)
        self.assertEqual(amt_OVL, 100)

    def test_px_mvt(self):
        '''price goes up, you should have more OVL when you get out
        '''
        #ETH is expensive rwt OVL: if ETH = $2000, then OVL = $20
        P0 = 100
        #ETH becomes twice as expensive rwt OVL: if ETH = $2000, then OVL = $10
        P1 = px_from_ret(P0, 100)

        amt_ETH_P0 = fromOVL(amt_OVL, P0)
        amt_ETH_P1 = fromOVL(amt_OVL, P1)
        self.assertTrue(np.isclose(amt_ETH_P0, 2*amt_ETH_P1))

        #ETH becomes half as expensive rwt OVL: if ETH = $2000, then OVL = $40
        P2 = px_from_ret(P0, -50)

        amt_ETH_P2 = fromOVL(amt_OVL, P2)
        self.assertTrue(np.isclose(amt_ETH_P0, .5*amt_ETH_P2))

    def test_value(self):
        '''
     the current value in ETH terms of our 1x long Overlay contract is
    \\[ V(t) = \frac{N(t)}{P(t)} \cdot \bigg[ 1 + \frac{P(t) - P_0}{P_0} \bigg].\\]
        '''
        #fix value N(t) = N = amt_OVL
        V = lambda P1, P0: (amt_OVL/P1)*(1 + (P1-P0)/P0)

        #ETH is expensive rwt OVL: if ETH = $2000, then OVL = $20
        P0 = 100
        self.assertTrue(V(P0,P0) == toETH(amt_OVL, P0))
        #ETH becomes twice as expensive rwt OVL: if ETH = $2000, then OVL = $10
        P1 = px_from_ret(P0, 100)
        self.assertTrue(V(P1,P0) == toETH(amt_OVL, P0))
        #ETH becomes 1/2 as expensive rwt OVL: if ETH = $2000, then OVL = $40
        P2 = px_from_ret(P0, -50)
        self.assertTrue(V(P2,P0) == toETH(amt_OVL, P0))


    def test_funding_formula(self):
        '''
        For our long position, the time evolution of our position size when factoring in funding payments is

        \\[ N(t) = n \cdot \prod_{i=0}^{m-1} \bigg[ 1 + f_l(i) \bigg] \\]
        '''
        for k in np.arange(.01, .5, .1):
            for iter_oi_long in np.arange(1,100,10):
                for iter_oi_short in np.arange(1, 100, 10):
                    oi_long = iter_oi_long
                    oi_short = iter_oi_short

                    all_funding_payments = []
                    all_funding_rates_short = []
                    all_funding_rates_long = []

                    for i in range(100): #100 funding payments
                        imb = get_imbalance(oi_long, oi_short)

                        all_funding_rates_short.append(funding_rate(k, imb, oi_short))
                        #NOTE: need negative sign to capture direction of funding
                        all_funding_rates_long.append(-funding_rate(k, imb, oi_long))

                        payment = funding(k, imb)
                        all_funding_payments.append(payment)

                        oi_long -= payment
                        oi_short += payment

                    F = sum(all_funding_payments)

                    all_funding_returns_short = [1 + r for r in all_funding_rates_short]
                    all_funding_returns_long = [1 + r for r in all_funding_rates_long]

                    final_oi_short = iter_oi_short*(np.prod(all_funding_returns_short))
                    final_oi_long = iter_oi_long*(np.prod(all_funding_returns_long))

                    self.assertTrue(np.isclose(iter_oi_short + F, final_oi_short))
                    self.assertTrue(np.isclose(iter_oi_long - F, final_oi_long))


    def test_short_payoff(self):
        '''
        Payoff for the 1x short is
        \\[ \mathrm{PO}(t) = \frac{N(t)}{2} \cdot \bigg[ 1 - \frac{P(t) - P_0}{P_0} \bigg] \\]
        '''
        V = lambda P1, P0: amt_OVL/2 * (1 - (P1 - P0)/P0)
        #ETH is expensive rwt OVL: if ETH = $2000, then OVL = $20
        P0 = 100
        self.assertTrue(V(P0,P0) == amt_OVL/2)
        #ETH becomes twice as expensive rwt OVL: if ETH = $2000, then OVL = $10
        #we should have 0 OVL left
        P1 = px_from_ret(P0, 100)
        self.assertTrue(V(P1,P0) == 0)
        #ETH becomes 1/2 as expensive rwt OVL: if ETH = $2000, then OVL = $40
        #we should get a return of 50% on our OVL
        P2 = px_from_ret(P0, -50)
        self.assertTrue(V(P2,P0) == 1.5*amt_OVL/2)

    def test_short_eth_value(self):
        '''
        and value of the spot ETH in OVL terms at time \\( t\\) is \\( (n / 2) \cdot (P(t) / P_0) \\).
        '''
        V = lambda P1, P0: amt_OVL/2 * (P1/P0)
        #ETH is expensive rwt OVL: if ETH = $2000, then OVL = $20
        P0 = 100
        self.assertTrue(V(P0,P0) == amt_OVL/2)
        #ETH becomes twice as expensive rwt OVL: if ETH = $2000, then OVL = $10
        #we should have 100 OVL in ETH
        P1 = px_from_ret(P0, 100)
        self.assertTrue(V(P1,P0) == amt_OVL)
        #ETH becomes 1/2 as expensive rwt OVL: if ETH = $2000, then OVL = $40
        #we should get a return of 50%  in OVL terms
        P2 = px_from_ret(P0, -50)
        self.assertTrue(V(P2,P0) == amt_OVL/4)



if __name__ == '__main__':
    unittest.main()


