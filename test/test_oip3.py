import typing as tp
import numpy as np
from util import *
import unittest
import pytest


amt_OVL = 100

def payoff(amt, side, leverage, p0, pt):
    return amt*(side*leverage*(pt/p0 - 1) + 1)

def pnl_hedged(
        amt,
        px,
        side,
        q,
        leverage_X,
        leverage_E,
        epsilon_X,
        epsilon_E):
    return (amt/px)*(side*q*leverage_X*epsilon_X  \
            + epsilon_E*(leverage_E *(1-q) - 1))

def pnl_unhedged(
        amt,
        px,
        side,
        leverage_X,
        epsilon_X,
        epsilon_E):
    return (amt/px)*(side*leverage_X*epsilon_X - epsilon_E)




class TestOIP1(unittest.TestCase):

    # @classmethod
    # def setUpClass(cls):
    #     ...

    def test_payoff_X(self):
        '''This test is in OVL terms, we do not test ETH terms since the logic is transparent and tested elsewhere
        '''

        for leverage in [1,2,3]:
            #The price of X vs its base reference is high, it takes 200 of the reference tokens (USD) to buy 1 of the X token. We imagine then the price goes to 300 and 100
            P0 = 200

            Pt1 = px_from_ret(P0, 50)
            #if we are long we should have 100 + 50 * leverage OVL
            self.assertEqual(payoff(amt_OVL, 1, leverage, P0, Pt1), amt_OVL + (50*leverage))
            #if we are short we should have 100 - 50 leverage OVL
            self.assertEqual(payoff(amt_OVL, -1, leverage, P0, Pt1), amt_OVL - (50*leverage))

            Pt2 = px_from_ret(P0, -50)
            self.assertEqual(payoff(amt_OVL, 1, leverage, P0, Pt2), amt_OVL - (50*leverage))
            self.assertEqual(payoff(amt_OVL, -1, leverage, P0, Pt2), amt_OVL + (50*leverage))

    def test_concrete_numbers_1(self):
        PX_0 = 3 #price of feed X at t = 0
        PE_0 = 1
        q = .8
        leverage_E = 5
        leverage_X = 1
        expected_results = {
                (10, 'unhedged', 'OVL'): 110,
                (10, 'unhedged', 'ETH'): 104.76,
                (10, 'hedged', 'OVL'): 113,
                (10, 'hedged', 'ETH'): 107.62,
                (20, 'unhedged', 'OVL'): 120,
                (20, 'unhedged', 'ETH'): 96,
                (20, 'hedged', 'OVL'): 141,
                (20, 'hedged', 'ETH'): 112.8,
            }

        for X_ret, E_ret in ((10,5), (20, 25)):
            ###UNHEDGED
            case = 'unhedged'

            PX_1 = px_from_ret(PX_0, X_ret)

            #ETH and OVL at parity
            PE_1 = px_from_ret(PE_0, E_ret)

            V_OVL = pnl(amt_OVL, X_ret)
            self.assertTrue(np.isclose(
                V_OVL,
                expected_results[(X_ret, case, 'OVL')]))

            V_ETH = toETH(V_OVL, PE_1)
            PNL_ETH = pnl_unhedged(
                amt_OVL,
                PE_1,
                1, #side
                1, #q
                X_ret/100,
                E_ret/100)
            V_ETH1 = toETH(amt_OVL, PE_0) + PNL_ETH

            self.assertTrue(np.isclose(V_ETH, V_ETH1))
            self.assertTrue(np.isclose(
                round(V_ETH,2),
                expected_results[(X_ret, case, 'ETH')]))

            ######### HEDGED
            case = 'hedged'

            V_OVL_EO = payoff((1-q)*amt_OVL, 1, leverage_E,  PE_0, PE_1)
            V_OVL_X =  payoff(q*amt_OVL, 1, leverage_X, PX_0, PX_1)
            V_OVL = V_OVL_EO + V_OVL_X

            self.assertTrue(np.isclose(
                V_OVL,
                expected_results[(X_ret, case, 'OVL')]))

            V_ETH = toETH(V_OVL, PE_1)
            PNL_ETH = pnl_hedged(
                amt_OVL,
                PE_1,
                1,
                q,
                leverage_X,
                leverage_E,
                X_ret/100,
                E_ret/100)
            V_ETH1 = toETH(amt_OVL, PE_0) + PNL_ETH

            self.assertTrue(np.isclose(V_ETH, V_ETH1))
            self.assertTrue(np.isclose(
                round(V_ETH,2),
                expected_results[(X_ret, case, 'ETH')]))


if __name__ == '__main__':
    unittest.main()


