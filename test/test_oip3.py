import typing as tp
import numpy as np
from util import *
import unittest
import pytest




amt_OVL = 100

def payoff(amt, side, leverage, P0, Pt):
    return amt*(side*leverage*(Pt/P0 - 1) + 1)

class TestOIP1(unittest.TestCase):

    # @classmethod
    # def setUpClass(cls):
    #     ...

    def test_payoff_X(self):

        for leverage in [1,2,3]:
            #The price of X vs its base reference is high, it takes 200 of the reference tokens (USD) to buy 1 of the X token. We imagine then the price goes to 300 and 100
            P0 = 200

            Pt1 = px_from_ret(P0, 50)
            #if we are long we should have 100 + 50 * leverage OVL
            self.assertEqual(payoff(amt_OVL, 1, leverage, P0, Pt1), amt_OVL + (50*leverage))
            #if we are short we should have 100 - 50 leverage OVL
            self.assertEqual(payoff(amt_OVL, -1, leverage, P0, Pt1), amt_OVL - (50*leverage))

            Pt1 = px_from_ret(P0, -50)
            self.assertEqual(payoff(amt_OVL, 1, leverage, P0, Pt1), amt_OVL - (50*leverage))
            self.assertEqual(payoff(amt_OVL, -1, leverage, P0, Pt1), amt_OVL + (50*leverage))



    def test_payoff_E(self):
        '''
        Payoff in ETH terms for X feed positions is:
        \\[ \mathrm{PO}\_{X}(t) = \frac{q \cdot n}{P(t)} \cdot \bigg[ 1 + (\pm)\_{X} \cdot l_X \cdot \bigg( \frac{P\_X(t)}{P_X(0)} - 1 \bigg) \bigg] \\]

        '''
        PX0 = 3 #price of feed X at t = 0

        Pt = 100#price of ETH at t

        for s in (1, -1):
            for q in np.arange(0,1,.1):
                ...

if __name__ == '__main__':
    unittest.main()


