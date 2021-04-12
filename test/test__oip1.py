import typing as tp
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from collections import defaultdict
import unittest
import pytest

np.random.seed(seed=1)


#    px is the price of OVL-ETH,
#    if it is > 1, OVL is more valuable than ETH
#    ie it requres tyhat many OVL to buy 1 ETH

def fromETH(amt, px):
    return amt/px
def toETH(amt, px):
    return amt*px

def toOVL(amt, px):
    return fromETH(amt, px)
def fromOVL(amt, px):
    return toETH(amt, px)


def px_from_ret(px0: float, ret: float) -> float:
    '''get the new price given a return'''
    ret = ret/100
    return (ret + 1)*px0

def pnl(amt, ret):
    return amt * (1 + ret/100)


p0 = 1  #initial price
N = 100  #initial size in OVL

class TestOIP1(unittest.TestCase):

    def test_price(self):
        #ETH is expensive rwt OVL: if ETH = $2000, then OVL = $20
        P0 = 100
        #we have 100 OVL, we buy ETH, we expect to have 1 ETH
        amt_OVL = 100
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
        #ETH is expensive rwt OVL:
        P0 = 100

    def test_px_mvt(self):
        '''price goes up, you should have more OVL when you get out
        '''

        p1 = px_from_ret(p0, 100)
        new_amt = fromOVL(N, p0)
        new_amt = fromETH(N, p1)
        print(new_amt)
        self.assertTrue(np.isclose(new_amt, 2*N))

    @unittest.skip('fix')
    def test_util_fcns(self):
        assert fromOVL(N/2, p0) == 5
        assert fromETH(5, p0) == 50
        assert fromETH(fromOVL(N, p0), p0) == N
        assert fromOVL(fromETH(N, p0), p0) == N

        assert np.isclose(px_from_ret(p0, 50), .15)
        assert np.isclose(px_from_ret(p0, 200), .3)
        assert np.isclose(px_from_ret(p0, -50), .05)

        assert pnl(100, 50) == 150
        assert pnl(100, -50) == 50





