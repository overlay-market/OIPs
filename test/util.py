
def fromETH(amt, px):
    return amt*px
def toETH(amt, px):
    return amt/px

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

def get_imbalance(longs, shorts):
    return longs - shorts

def funding(k, imb):
    return k*imb

def funding_rate(k, imb, side_oi):
    '''side_oi is volume of long or short side'''
    return k*imb/side_oi
