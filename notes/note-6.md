---
note: 6 
oip-num: 1 
title: Pooling Stability Funds
status: WIP
author: Adam Kay (@mcillkay)
discussions-to: oip-1
created: 2021-04-17
updated: N/A
---

Issue to address with this note:

- How do we realize the potential for huge capital pools to stabilize the system by making yield on funding?

- How do we address the outstanding risk to the system that exists if funding is implemented as currently specified?

## Context

[A previous note](note-1) explored the ability of a funding payment mechanism to incentivize yield hunters to balance the Overlay system directional risk. These actors seek yield on either OVL, ETH, DAI (or some other cryptoasset), without taking directional risk. In this note they will be called *investors*. In practice there are some difficulties with the approach:


1. To remain profitable, investors must remain nimble, reacting quickly to changes in the imbalance. Failure to do so will reduce yield or even incur loss. Thus investors must be fairly high frequency.

2. As the system scales, investors who wish to gain yield must keep track of an increasing number of markets.

3. Moreover, small imbalances on multiple markets might not be worth balancing for investors individually, but collectively might represent a significant risk to the system.   

4. Investors competing to gather yield can all come in at the same time and overshoot the imbalance to the other side, causing them to pay rather than get paid. 

5. The funding mechanism as outlined in [OIP1](note-1) can only ever *damp* the risk to the system, never eliminate it. As currently described, investors are incentivized to make their balancing trades as small as possible. If we enforce a minimum amount, this must always be relatively small because the imbalance goes to zero as the balancing trades get large. 

6. Because of the above point it is entirely possible that, even with investors collecting yield, OI caps in one direction could be hit while prices move rapidly. In this case the Overlay system would  incur significant inflation risk. 

7. The idea of a contract which facilitates the required balancing trades, returning an ERC-20 token such as ✨ETH or ✨OVL (Magic ETH and Magic OVL), mentioned the possibility of users swapping 'into or out of on spot AMMs' or providing liquidity for 'exchanges specializing in like-asset pairs'. However for there to be a large amount of outstanding ✨ETH or ✨OVL, as currently specified, those trades would have to be placed on the relevant market, implying that 1) the caps on these markets will have to be made very large to accomodate 'balancing' liquidity and 2) the 'balancing' liquidity is no longer balancing but sitting there passively. 



<!-- 4. The stragegy that has investors gaining yield on OVL on the OVL-ETH feed requires them to first sell half their OVL for spot ETH. This becomes increasingly difficult as Overlay scales to many assets across multiple exchanges, and  it is impossible for non-financial markets such as pure scalar data feeds (e.g. the CPI). -->

<!-- tokenized trade -->

<!-- pThese are effectively tokenized basis trades that users can easily swap into or out of on spot AMMs as funding rates go against their respective side or provide liquidity for on spot exchanges specializing in like-asset pairs (e.g. Magic ETH & ETH pool). -->


These issues collectively assure that 1) the balancing mechanism will be a specialized activity, requiring ongoing maintenance and incurring technical debt, 2) the magic contracts as currently imagined do not escape issues 1-6 above, and because of issue 7 actually increase the risk to the system. 

Because the effectiveness of the funding mechanism is be a bottleneck for the system itself, unless these issues can be solved the system cannot scale. 

Fortunately, all of the above issues can be solved at one time, by slightly altering the specification of the magic contracts. 
## Passive Balancing Pools

### Summary

The basic idea is not to write contracts that enter the relevant positions for a user and issue ERC-20s, but rather which pool liquidity, issue ERC-20s, and then use that liquidity to *always* balance all markets. In this way *all* inflation risk to the Overlay system is completely eliminated, and scaling becomes a function of the liquidity in ✨ETH, ✨OVL and ✨DAI. 


<!-- To allow for an Overlay-managed pool, similar to a Yearn vault, which incurs zero transactions fees, takes the opposite side of the imbalance on *all* Overlay markets collectively, and allows for yield on both OVL and ETH. -->



### Basic Idea

Ideally, the funding rate mechanism should *insure* that the risk to the system is zero. This is far from the case as it is currently designed. By tweaking the funding mechanism slightly, however, this can be achieved.  From [OIP-1](note-1):


>Let the open interest contributed by any one position to the long (short) side be the number \\(N \\) of OVL locked to that side, times the leverage \\(L\\) associated with those \\(N\\)  OVL. Thus, for trader \\( j \\) going long (thus the subscript \\(l\\)) we have

>\\[ \mathrm{OI}\_{jl} = L_{jl} \cdot N_{jl}\\]


>The funding payment will probably be computed each oracle fetch rather than each block, as oracle times may vary by market and are a natural 'heartbeat'.  Consequently, let us assume there are \\(m \\) funding payments accrued between \\(t_0\\) and \\(t\\), and that each one takes place at some time \\(t_i\\) for \\(i = 1,2,\ldots,m\\). 

We will slightly alter notation and let \\(I(t) = \mathrm{OI}\_{imb}(t)\\), the imbalance at time $$t$$, and write $$I(t) = L(t) - S(t)$$, long minus short open interest at time $$t$$.

Assume at $$t_0$$ there are no trades and so $$L_0 = S_0 = I_0 = 0$$. Let the next oracle fetch be at \\(t^\* > t_0\\) and say there are $$h$$ blocks between $$t_0$$ and \\(t^\*\\). So according to the subscript notation where $$t_i$$ is the $$i^\mathrm{th}$$ oracle fetch and funding payment, we have \\(t_{0} + h = t_{1} = t^\* \\). 

During these $$h$$ blocks, say there are trades queued on both the long and short side. The sum of all these trades will make up $$I_1 = L_1 - S_1$$. The rational behavior for an investor trying to collect funding as currently designed is to wait until the last moment before $$t_1$$ and enter an offsetting trade. (Otherwise, how does the invesor know which side to come in on?) However, others may be doing the same thing and so there will be competition, driving up the gas the investors have to pay, with potential bad effects including 1) overshoot as multiple investors make offsetting trades and wind up *paying* funding next block rather than collecting it, or 2) minimal balancing as investors seek to balance with the smallest possible amount that is still cost effective. 

Say the balancing trades that come in from investors represent $$B$$ open interest. Then we will have $$ \mathrm{abs}(L_1 - S_1) > \mathrm{abs}(L_1 - S_1 \pm B_1)$$, if there is no overshoot. If there is overshoot the sign of $$I_1$$ can be opposite (and abs($$I$$) may even be greater i.e. worse) than it would have been if there were no investors. 

<!-- The way the funding payments work currently is that one user pays gas to settle *all* trades in the queue as well as funding payments. --> 
The brute force way of making funding payments involves looping over each address's position and shrinking or growing it accordingly. If there are $$m$$ longs and $$n$$ shorts, then this is $$mn$$ writes. As the system scales with large caps on popular markets, this becomes too expensive. Another (better) way is to do a single write and save the funding *rate* at each block as a signed int, and then each time a trader exits a position, read back through the history of funding payments they would have received using the brute force method, and sum them. Of course, if this can be done, we can write nothing, and simply look at the imbalance at each block and compute the funding rate dynamically upon unwind. 

This observation shows that computing balances upon entry and exit of positions *as though* the mechanism operated in real-time is desireable, and of course the more gas-efficient we can make the system generally the better. We should therefore have a bias towards virtualizing any transactions that we can.  

Another important observation is that we can currently not say whether a last-minute position represents an investor or someone taking directional risk. However, the entire idea of funding payments is predicated on a discinction between such 'traders' and investors. The latter do not want directional risk and want yield. The funding payments are currently set up to not distinguish between traders and investors at all, and this may be desireable. However, it is by no means *a priori* undesirable to make the distinction at the system level. 

### Details
Let us now assume that we have a pool of ✨DAI. Depositors into the magic DAI contract will now be identified exclusively with investors, while anyone taking position on DAI-OVL market will be a trader. Define a constant $$\beta \in (0,1]$$ that will determine how much of the funding goes to traders reducing imbalance, and how much goes to investors, who will *eliminate* the remainder. When $$\beta = 1$$ all of the funding goes to the investors.  We will abstract away the side of ✨DAI, though of course the denomination of the underlying contract depends on the side it is balancing on DAI-OVL to get yield. 

For simplicity, assume the scenario above with $$L_0 = 0 = S_0$$, and let $$L_1 \neq 0 = S_1$$, and set $$\beta = 1$$. All the imbalance is on the long side, and no traders are shorting (maybe ETH is mooning). The funding payment for this period over $$h$$ blocks will be $$kL_1$$. Say at the next oracle fetch a trader exits, whose position is $$.1L_1$$. She pays gas to make four things happen: 

1. her position is unwound -- this is the standard behavior of the market contract which we need anyway. 

2. the oracle is updated -- this we also need and are planning to implement.  

3. funding is paid to ✨DAI -- this is new, the trader pays to transfer $$.1kL_1$$ from her own OVL balance to ✨DAI. 

4. the ✨DAI pool shrinks/grows -- this is new, it is *as though* the ✨DAI pool had entered a short position on DAI-OVL at the last possible moment, with size $$S_1 = L_1$$, perfectly balancing the book. 

The above example can be generalized to any case where $$L_1 > S_1$$. If $$S_1 > L_1$$, then it is ✨OVL that plays the balancing role.  

Now let us imagine a scenario where $$\beta \neq 1$$. 


One interesting feature of this idea is that, because OVL is the settlement currency, ✨OVL is special in several ways. We list them here:

1. A *massive* amount of short pressure be exerted on it via hedging, thus creating juicy yields for ✨OVL holders.

2. Any new X market that we list is an X-OVL market, which means that the ✨OVL pool automatically can get yield from traders going short there. Thus, the more markets we list, the greater the yield for ✨OVL, driving capital into ✨OVL, allowing us to list more markets.  

3. The capacity of the protocol as a whole is limited by the depth of ✨OVL, so we may use this depth as a parameter to optimize when thinking about  scaling.




(we may be able to not do this last one if the depth of the ✨DAI pool can be computed dynamically at each oracle fetch).  

this is important to do rather when deposits/withdrawals happen in the ✨DAI contract, so the size of ✨DAI is known at the time of trading.)

Specifically, ✨DAI is shrunk or grown to reflect price movements since the last fetch, and then $$.1kL_1$$ OVL is deposited from the trader's position into ✨DAI. 

The ✨DAI pool is a passive pool that does not make calls to the standard market contract. Nobody pays gas to enter positions. It never overshoots because it always balances the correct amount to eighteen decimal places. Using this balancing mechanism, the caps on the X market are actually equivalent to the depth of the ✨DAI pool, which could conceivably be extremely deep, many billions worth of USD. If there is little volume on X, the yield will be low and X will be shallow, but that is fine because there is litle volume, so not much risk to balance. If there is a lot of volume, ✨DAI will have high yield and attract deeper capital. It is exactly the kind of postiive feedback loop we want. Most importantly, this mechanism *completely eliminates* all inflation risk for the X market. With this mechanism in place, OVL will never inflate through X risk. It will only deflate (and likely a lot) as people lose, get liquidated, and pay fees. Because OVL becomes deflationary on the X market, more OVL can be given to LPs, increasing utility and thus volume, and thus yield in ✨DAI pools.   

This works! This is the coolest possible solution to the inflation problem.

<!-- to ever hit Overlay! And it's a combination of three brilliant ideas! --> 
<!-- FP(m) = k(m)I(m) -->

<!-- These will likely be tracked by a single scalar variable which determines how much --> 











<!-- On ETH-OVL market, someone opens a long position of $$n$$ OVL (effectively selling OVL and buying ETH). In order to balance this position, the pool would need to short the same feed with size $$\alpha n$$ for some $$0 < \alpha < 1$$ selected for optimal returns. However, in order to enter a short trade on ETH-OVL, the investor must first sell half of her OVL for ETH on spot. Thus to balance the investor needs $$2 \alpha n$$, where half of this is actually being held in ETH. -->

<!-- Case 1a: After $$m$$ oracle fetches, someone else comees on the other side, partially the pool. Their trade triggers the -->

<!-- Case 1b: After $$m$$ oracle fetches, someone else comees on the other side, with OI greater than the current imbalance, creating a balance to the other wise. The imbalance is system then behaves as though the passive pool holders now switch their positions. When another transaction is made, -->

<!-- The tuple $$(\iota , \tau)$$ stands for imbalance, and time (be it block time, oracle fetch time, or what have you). -->

<!-- 0. Some transaction on market is made at time $$t$$. -->  

<!-- 1. Read $$(\iota, \tau)$$. -->

<!-- 2. The passive pool is considered to have been trading the market alongside the $p$ traders, with size $$\alpha \iota$$. For example, $$\alpha = .33\$$. Compute the "virtual imbalance" -->  
<!-- \\[\\] -->

<!-- If $$\iota \neq 0$$, compute funding payments between $\tau$ and $$t$$. Say $$m$$ oracle fetches have occurred between $$\tau$$ and $$t$$. So the funding is -->
<!-- \\[ F = \iota (1-2k)^m\\] -->

<!-- 3. Distribute $F$ pro rata between the $p$ traders as follows. Say $$\sum N_{ai} = P$$. Then we must have $$OI_{\hat{a}} - P = \iota$. -->


<!-- 4. Funding is distributed among $p$ traders and the passive pool according to: -->
<!-- . , compute new $$(I, t)$$ and . -->   

<!-- 1. If $$ I  \neq 0$$, then $$I$$ and update block (or oracle fetch number) are saved as attributes to market. -->

<!-- 2. f -->




<!-- partially the pool. Their trade triggers the -->
<!-- Case 2: -->

<!-- No trades or transactions are made. The positions are "virtual" in the sense that by investing in the pool, the investors are agreeing to balance all open markets. -->

<!-- ### Liquidation -->

<!-- The risk is that , thus caps can be set -->  

<!-- The rebalancings -->

<!-- ### Example -->

<!-- Overlay has 1k active markets. Each of them are slightly unbalanced to the long side, but not enough for funding to pay for the fees to get in and out of the balancing trades. -->  

<!-- Overlay has 1 market that is *never* balanced. For whatever reason, nobody ever takes the other side. -->
