---
note: 13 
oip-num: 1 
title: Upgrade to OIP-6 "Pooling Stability Funds"
status: WIP
author: Adam Kay (@mcillkay)
discussions-to: oip-6
created: 2022-05-11
updated: N/A
---

Issue to address with this note:

- How do we realize the potential for huge capital pools to stabilize the system by making yield on funding?


## Context

[A previous note](note-6) explored the ability a modification of the  funding payment mechanism to ameliorate some of the design downsides to the mechanism. Recent developments with discussions around allowing basis trading on permissionless lending pools have given this idea new life. We here explore the consequences of combining stability pools of yield seeking basis users with smart contracts internal to the Overlay system. 


[OIP-1](note-1) had previously described how those denominating in OVL can ameliorate  bearish  OI imbalance  (those going long the inverse X-OVL market), and those denominating in X can ameliorate bullish OI imbalance (those shorting X-OVL). The main concern with this limitation is that it relies on having bullish OVL sentiment, but this can evaporate precisely when you need it the most (a meltdown of OVL price).  Michael realized that a lending pool of Y-OVL allows investors who prefer to denominate in Y (ETH, DAI, etc.) to stabilize the Overlay system by entering the basis position on *either* side of the imbalance.


Assume we have a lending pool of Y-OVL, just called the *pool*. Likewise assume there is imbalance on some X-OVL market on the Overlay system. 

<!-- 4. The stragegy that has investors gaining yield on OVL on the OVL-ETH feed requires them to first sell half their OVL for spot ETH. This becomes increasingly difficult as Overlay scales to many assets across multiple exchanges, and  it is impossible for non-financial markets such as pure scalar data feeds (e.g. the CPI). -->

<!-- tokenized position -->

<!-- pThese are effectively tokenized basis positions that users can easily swap into or out of on spot AMMs as funding rates go against their respective side or provide liquidity for on spot exchanges specializing in like-asset pairs (e.g. Magic ETH & ETH pool). -->


Problem 1.1 entails that OI caps in one direction could be hit while prices move rapidly. The OVL supply would  then  inflate significantly. Thus, in extreme cases, the funding mechanism does not fulfil its primary purpose.  

The issues collectively seem significant.  Because the effectiveness of the funding mechanism is  a bottleneck for the system itself, unless these issues can be solved the system cannot scale. 

Fortunately, all but one of the above issues can be solved at one time, by distinguishing between users and investors. Before presenting the solution, however, we show why we *must* distinguish between them.


<!-- , by slightly altering the specification of the magic contracts. --> 

<!-- These issues collectively assure that 1) the balancing mechanism will be a specialized activity, requiring ongoing maintenance and incurring technical debt, and yields will not be as good as they might be, thus limiting the appeal, and  2) the magic contracts as currently imagined do not escape issues 1-6 above, and because of issue 7 actually increase the risk to the system. --> 



<!-- To allow for an Overlay-managed pool, similar to a Yearn vault, which incurs zero transactions fees, takes the opposite side of the imbalance on *all* Overlay markets collectively, and allows for yield on both OVL and ETH. -->



#### Parasitic Capital
Problem 2.4 makes it imperative to distinguish between users and investors. To get the basic idea across, pretend for a moment that there are *two* users on DAI-OVL. One has gone long with size $$n$$, and the other has gone long *and* short, both with size $$N>n$$. The imbalance is $$n$$, and after one funding period the longs must pay $$kn$$, which goes to the short side. In that time, say DAI-OVL rose by $$r$$ percent. To update PnL, there will be two `mint` and one `burn` calls to the market contract, plus whatever calls are made to effect funding transfers.  The first user has 
\\[n\Big(1 +r - kn\frac{n}{n+N}\Big)\\]
while the second user  has
\\[N\Big(1 +r - kn\frac{N}{n+N}\Big) + N(1 - r + kn) = 2N + kn\frac{n}{n+N}\\]

This shows that funding can be collected passively without being nimble or even worrying about trading, by simply taking the long and short side in equal parts. This is a weakness of the current funding mechanism since it represents parasitic capital. There is every reason to think that a significant amount  of OI will  be given over to this type of position. 

## Passive Balancing Pools


Funding must flow from OI on the market contract to OI on a different type of contract, to which investors which balance user OI will deposit. What should the investor contract  look like? 



It is clear that we cannot have passive pools of locked OVL tracking the value of OVL, DAI, or ETH, because this simply shifts the inflation problem to the investor pools. Since these pools are likely to be large, the problem would be worse. Thus, we need pools of unlocked OVL, along with pools of  DAI and ETH (and WBTC and any other base currency we care to list). 


In fact, the idea of magic tokens is almost the same as a passive balancing pool.  The way the magic contracts would work as proposed in [OIP-1](note-1) would be to automate the swaps and Overlay calls required to enter balancing positions. It is clear that these swaps must be entered and exited opportunistically, each funding period. The majority of the magic pools would be passively sitting, denominated in OVL, ETH, and DAI, while a small amount of it would be deployed at any time to balance user OI. 

If the funding mechanism is implemented as currently specified, the magic tokens are subject to all the problems above. However, since a distinction between users and investors is forced on us, we may treat the investors differently than the users. This represents no system risk since all investor positions are automated by our contracts. 

If the Overlay system allowed the magic contracts to make swaps *immediately after* an oracle fetch and receive the *last* price (rather than the next one, as users using the market contract would receive), then the imbalance could be eliminated entirely. More precisely, the logic would be:

1. Users taking positions using the market contract generate an imbalance $$I$$ after the oracle fetch at $$t_0$$, getting price $$P_0$$.

2. On block $$t_0 + 1$$, the magic contract makes the required swaps on an AMM. If $$I>0$$ then ETH or DAI is sold for $$I$$ worth of OVL.  Otherwise $$I$$ OVL is sold for ETH or DAI. The price $$P_0$$ is saved and associated with this swap. 

3. Whenever a user unwinds at price $$P(t)$$, the return $$nr$$ to this user is not generated from a `mint` or `burn` call, but a `transfer` call, either from the $$I$$ OVL held by the magic contract, or to it. 

4. The magic contracts exit their positions gradually as imbalance changes, or all at once as it changes sign.  


### Discussion
The funding mechanism has promise but requires significant tuning to fulfil its purpose. The main problems are 1.1 (imbalance can never go to zero), 2.4 (parasitic capital) and all problems 5 (the mechanism is beset with negative feedback). 


All of these problems are bugs resulting from the failure to separate users and investors. Once this separation is forced on us (which it is), it is clear that *all* funding must flow  from users to investors. This will probably require the funding rate to be lower, since users are never collecting funding. The $$k$$ constant can be tuned depending on user and investor behavior (rather than, or in addition to, the current factors involved in tuning). 

Luckily, separating users and investors allows us to resolve problems 1, 2, 3, and 5, and all their subproblems.  One of the most significant results of this mechanism is that problem 1.1 is resolved. The risk to the Overlay system on markets balanced by investors is zero. This solves the inflation problem completely. 

Another very significant result is that the negative feedback of problem 5 becomes positive feedback. Investors do not need to be nimble to make yield, resulting in fewer fees and thus higher yield. There is no fee competition or overshoot. The more the system scales, the larger the yield opportunity with the *same* level of technical debt. Most significantly, it is clear that the OI caps for the users should be identified with the depth of the passive pools. Since these pools are likely to be large, the user caps can be large, increasing volume, and thus increasing yield, and thus increasing pool depth in a positive feedback loop. 

<!-- (Payout OI should be a function of OVL-ETH and OVL-DAI liquidity on AMMs) -->

The last problem (#4) involves the expense of making four positions to collect funding, along with the concomitant front-running into and out of OVL on an AMM that is sure to emerge. This may be unavoidable. In any case we leave it to a future discussion. 

<!-- How can we resolve this? -->

<!-- There are different types of solution. --> 

<!-- 1. Force all investors to deposit certain proportions of OVL, ETH and DAI, creating some  impermanent loss risk. --> 

<!-- 2. Allow automated lending between the pools, creating some price exposure risk. --> 








<!-- [OIP-1](note-1) presented the idea of a contract which facilitates the required balancing positions, returning an ERC-20 token such as meth or mOVL (Magic ETH and Magic OVL).  mentioned the possibility of users swapping 'into or out of on spot AMMs' or providing liquidity for 'exchanges specializing in like-asset pairs'. The solution to the above funding problems is evident by focusing on the special nature of the  mOVL pool. -->
<!-- <!-1- However for there to be a large amount of outstanding mETH or mOVL, as currently specified, those positions would have to be placed on the relevant market, implying that 1) the caps on these markets will have to be made very large to accomodate 'balancing' liquidity and 2) the 'balancing' liquidity is no longer balancing but sitting there passively. -1-> --> 

<!-- Holders of mOVL want yield on OVL without incurring price risk. Each mOVL is focused on a specific pair, e.g. OVL-DAI, OVL-ETH, OVL-WBTC. For simplicity we will identify mOVL in this note with the OVL-DAI pair. The relevant position is able to provide balance on the *long* side of OVL-DAI (buying OVL when most volume is shorting it) only, and it hedges price risk by selling half into DAI on spot. --> 

<!-- An equivalent position purely on the Overlay system would be to short OVL-DAI with half the stack and long it with the other half. Of course then funding cannot be collected because the imabalance is not altered by this position. However, if we make mOVL holders 'first-class citizens' we iare able to solve most of the problems listed above. In fact we can see that many of them are created by a refusal to distinguish between users and investors. -->  

<!-- The basic idea is not to write contracts that enter the relevant positions for a user and issue ERC-20s, but rather which pool OVL liquidity, and then replace `mint` and `burn` calls with built-in `transfer` calls. This solution has positive feedback features which leads to a virtuous cycle, and promises a mature system that  *always* balance all markets. In this end state, *all* inflation risk to the Overlay system is completely eliminated, and scaling becomes a function of the liquidity in mOVL. --> 
<!-- ## Basic Idea of Passive Pools -->
<!-- Because investors have more money and seek yield on huge pools of capital, they will want to go long and short very large. However, OI caps are built for users, and at all times we must assume that the entirety of one side will cancel. Thus the OI caps must be relatively small. The more investors crowd out users, furthermore, the less reason there is for them to do so. --> 

<!-- What we propose here is to distinguish between users and investors. We will have two separate contracts for them. The imbalance is still $$n$$, but now there is only $$n$$ OVL locked, so the first user pays *all* of the funding. Under the hood, we --> 
<!-- replaced the two `mint` and one `burn` calls  with one `mint`, one `burn` and one `transfer` call, so that the $$nr$$ OVL won by the first user comes from the second user's loss. (We still have a burn call because $$N>n$$.) If we can balance the sizes of offsetting positions (roughly, speaking, so $$N = n$$), then we can avoid `mint` and `burn` calls and only use `transfer`. If passive balancing pools can work, the OVL gets transferred around just as in a traditional CEX. --> 

<!-- In this picture, the  first user would have -->
<!-- \\[n(1 +r - kn)\\] -->
<!-- while the second user would have --> 
<!-- \\[2N + kn.\\] -->


<!-- ### Specific Idea -->

<!-- Ideally, the funding rate mechanism should *insure* that the risk to the system is zero. This is far from the case as it is currently designed. By tweaking the funding mechanism slightly, however, this can be achieved.  From [OIP-1](note-1): -->


<!-- >Let the open interest contributed by any one position to the long (short) side be the number \\(N \\) of OVL locked to that side, times the leverage \\(L\\) associated with those \\(N\\)  OVL. Thus, for user \\( j \\) going long (thus the subscript \\(l\\)) we have -->

<!-- >\\[ \mathrm{OI}\_{jl} = L_{jl} \cdot N_{jl}\\] -->


<!-- >The funding payment will probably be computed each oracle fetch rather than each block, as oracle times may vary by market and are a natural 'heartbeat'.  Consequently, let us assume there are \\(m \\) funding payments accrued between \\(t_0\\) and \\(t\\), and that each one takes place at some time \\(t_i\\) for \\(i = 1,2,\ldots,m\\). --> 

<!-- We will slightly alter notation and let \\(I(t) = \mathrm{OI}\_{imb}(t)\\), the imbalance at time $$t$$, and write $$I(t) = L(t) - S(t)$$, long minus short open interest at time $$t$$. -->

<!-- Assume at $$t_0$$ there are no positions and so $$L_0 = S_0 = I_0 = 0$$. Let the next oracle fetch be at \\(t^\* > t_0\\) and say there are $$h$$ blocks between $$t_0$$ and \\(t^\*\\). So according to the subscript notation where $$t_i$$ is the $$i^\mathrm{th}$$ oracle fetch and funding payment, we have \\(t_{0} + h = t_{1} = t^\* \\). --> 

<!-- During these $$h$$ blocks, say there are positions queued on both the long and short side. The sum of all these positions will make up $$I_1 = L_1 - S_1$$. The rational behavior for an investor trying to collect funding as currently designed is to wait until the last moment before $$t_1$$ and enter an offsetting position. (Otherwise, how does the invesor know which side to come in on?) However, others may be doing the same thing and so there will be competition, driving up the gas the investors have to pay, with potential bad effects including 1) overshoot as multiple investors make offsetting positions and wind up *paying* funding next block rather than collecting it, or 2) minimal balancing as investors seek to balance with the smallest possible amount that is still cost effective. --> 

<!-- Say the balancing positions that come in from investors represent $$B$$ open interest. Then we will have $$ \mathrm{abs}(L_1 - S_1) > \mathrm{abs}(L_1 - S_1 \pm B_1)$$, if there is no overshoot. If there is overshoot the sign of $$I_1$$ can be opposite (and abs($$I$$) may even be greater i.e. worse) than it would have been if there were no investors. --> 

<!-- <!-1- The way the funding payments work currently is that one user pays gas to settle *all* positions in the queue as well as funding payments. -1-> --> 
<!-- The brute force way of making funding payments involves looping over each address's position and shrinking or growing it accordingly. If there are $$m$$ longs and $$n$$ shorts, then this is $$mn$$ writes. As the system scales with large caps on popular markets, this becomes too expensive. Another (better) way is to do a single write and save the funding *rate* at each block as a signed int, and then each time a user exits a position, read back through the history of funding payments they would have received using the brute force method, and sum them. Of course, if this can be done, we can write nothing, and simply look at the imbalance at each block and compute the funding rate dynamically upon unwind. --> 

<!-- This observation shows that computing balances upon entry and exit of positions *as though* the mechanism operated in real-time is desireable, and of course the more gas-efficient we can make the system generally the better. We should therefore have a bias towards virtualizing any transactions that we can. -->  

<!-- Another important observation is that we can currently not say whether a last-minute position represents an investor or someone taking directional risk. However, the entire idea of funding payments is predicated on a discinction between such 'users' and investors. The latter do not want directional risk and want yield. The funding payments are currently set up to not distinguish between users and investors at all, and this may be desireable. However, it is by no means *a priori* undesirable to make the distinction at the system level. --> 

<!-- ### Details -->
<!-- Let us now assume that we have a pool of mDAI. Depositors into the magic DAI contract will now be identified exclusively with investors, while anyone taking position on DAI-OVL market will be a user. Define a constant $$\beta \in (0,1]$$ that will determine how much of the funding goes to users reducing imbalance, and how much goes to investors, who will *eliminate* the remainder. When $$\beta = 1$$ all of the funding goes to the investors. --> 

<!-- For simplicity, assume the scenario above with $$L_0 = 0 = S_0$$, and let $$L_1 \neq 0 = S_1$$, and set $$\beta = 1$$. All the imbalance is on the long side, and no users are shorting. The funding payment for this period over $$h$$ blocks will be $$kL_1$$. Say at the next oracle fetch a user exits, whose position is $$.1L_1$$. She pays gas to make four things happen: --> 

<!-- 1. her position is unwound -- this is the standard behavior of the market contract which we need anyway. --> 

<!-- 2. the oracle is updated -- this we also need and are planning to implement. -->  

<!-- 3. funding is paid to mDAI -- this is new, the user pays to transfer $$.1kL_1$$ from her own OVL balance to mDAI. --> 

<!-- 4. the mDAI pool shrinks/grows -- this is new, it is *as though* the mDAI pool had entered a short position on DAI-OVL at the last possible moment, with size $$S_1 = L_1$$, perfectly balancing the book. --> 

<!-- The above example can be generalized to any case where $$L_1 > S_1$$. If $$S_1 > L_1$$, then it is mOVL that plays the balancing role. -->  

<!-- Now let us imagine a scenario where $$\beta \neq 1$$, and $$S_1 \neq 0$$, but we still have $$I_1 > 0$$. In this case funding is still paid to mDAI, but some of it goes to the users on the short side as well. It seems reasonable to pay funding to everyone on a pro-rata basis as originally designed. In this case $$\beta$$ would change each oracle fetch, and for the $$m^\mathrm{th}$$ funding payment, can be computed as --> 

<!-- \\[\beta(m) = \pm\frac{I(m)}{G(m)}\\] -->

<!-- where $$G=L$$ if $$L>S$$ and otherwise $$G=S$$, and the sign changes to negative if $$G = S$$. --> 

<!-- Thinking about $$\beta$$ is helpful to determine how we wish to distribute funding payments, and to what degree we want users to benefit from funding payments as well as paying them. It seems desireable that users should receive funding, since it makes them more likely to also pay it. --> 

<!-- ### Conclusions -->
<!-- One interesting feature of this idea is that, because OVL is the settlement currency, mOVL is special in several ways: -->

<!-- 1. A *massive* amount of short pressure will be exerted on ETH-OVL and especially DAI-OVL via hedging, thus creating juicy yields for mOVL holders. -->

<!-- 2. Any new X market that we list is an X-OVL market, which means that the mOVL pool automatically can get yield from users going short there. Thus, the more markets we list, the greater the yield for mOVL, driving capital into mOVL, allowing us to list more markets. -->  

<!-- 3. The capacity of the protocol as a whole is limited by the depth of mOVL, so we may use this depth as a parameter to optimize when thinking about  scaling. -->


<!-- Finally, we will briefly explain how this idea addresses all of the problems above: --> 

<!-- 1. ✅ Investors are now passive rather than high frequency, and incur zero fees. -->
<!-- 2. 1/2✅ Investors in mOVL are automatically exposed to all markets as the system scales (although, those wishing to get yield on the other side still need to keep track of a multitude of magic pools). -->  
<!-- 3. 1/2✅ Small imbalances on multiple markets on the short side are automatically balanced by mOVL, and are balanced on the long side if there are magic pools for those markets. -->
<!-- 4. ✅ There is no overshoot. --> 
<!-- 5. ✅ Funding is improved from a mere damping mechanism, and investors are no longer incentivized to balance with the smallest possible amount. --> 
<!-- 6. ✅ The inflation risk to Overlay is completely mitigated on markets that have magic pools. --> 
<!-- 7. ✅ As magic tokens do not increase OI, there can be pools of arbitrary depth. Rather than *increasing* the risk to Overlay, these now decrease it, as desired. --> 


<!-- A few final thoughts: --> 

<!-- Using this balancing mechanism, the caps on the DAI-OVL market are actually equivalent to the depth of the mDAI pool, which could conceivably be extremely deep, many billions worth of USD. If there is little volume on DAI-OVL, the yield will be low and mDAI will be shallow, but that is fine because there is litle volume, so not much risk to balance. If there is a lot of volume, mDAI will have high yield and attract deeper capital. It is exactly the kind of positive feedback loop we want. --> 

<!-- Most importantly, this mechanism *completely eliminates* all inflation risk for the DAI-OVL market (assuming that we also have a deep mOVL pool).  With this mechanism in place, OVL will never inflate through DAI-OVL risk. It will only deflate, and likely a lot, as people lose, get liquidated, and pay fees. Because OVL becomes deflationary on the DAI-OVL market, more OVL can be given to LPs, increasing utility and thus volume, and thus yield in mDAI pools. This also completely eliminates the death spiral (on this market). Thus, there is no reason not to hold mOVL, thus we can concieve of a very very deep mOVL, thus the system can scale. --> 


<!-- Finally, this points the way to a very attractive future, a decentralized protocol that acts as a decentralized exchange, where fees and funding payments, instead of going to a centralized exchange, go to the LPs, magic token holders, and OVL holders. A system with significant volume like this enters a virtuous feedback loop which can scale and generate enormous revenues. --> 


<!-- ## This works! This is the coolest possible solution to the inflation problem. -->

<!-- to ever hit Overlay! And it's a combination of three brilliant ideas! --> 
<!-- FP(m) = k(m)I(m) -->

<!-- These will likely be tracked by a single scalar variable which determines how much --> 











<!-- On ETH-OVL market, someone opens a long position of $$n$$ OVL (effectively selling OVL and buying ETH). In order to balance this position, the pool would need to short the same feed with size $$\alpha n$$ for some $$0 < \alpha < 1$$ selected for optimal returns. However, in order to enter a short position on ETH-OVL, the investor must first sell half of her OVL for ETH on spot. Thus to balance the investor needs $$2 \alpha n$$, where half of this is actually being held in ETH. -->

<!-- Case 1a: After $$m$$ oracle fetches, someone else comees on the other side, partially the pool. Their position triggers the -->

<!-- Case 1b: After $$m$$ oracle fetches, someone else comees on the other side, with OI greater than the current imbalance, creating a balance to the other wise. The imbalance is system then behaves as though the passive pool holders now switch their positions. When another transaction is made, -->

<!-- The tuple $$(\iota , \tau)$$ stands for imbalance, and time (be it block time, oracle fetch time, or what have you). -->

<!-- 0. Some transaction on market is made at time $$t$$. -->  

<!-- 1. Read $$(\iota, \tau)$$. -->

<!-- 2. The passive pool is considered to have been trading the market alongside the $p$ users, with size $$\alpha \iota$$. For example, $$\alpha = .33\$$. Compute the "virtual imbalance" -->  
<!-- \\[\\] -->

<!-- If $$\iota \neq 0$$, compute funding payments between $\tau$ and $$t$$. Say $$m$$ oracle fetches have occurred between $$\tau$$ and $$t$$. So the funding is -->
<!-- \\[ F = \iota (1-2k)^m\\] -->

<!-- 3. Distribute $F$ pro rata between the $p$ users as follows. Say $$\sum N_{ai} = P$$. Then we must have $$OI_{\hat{a}} - P = \iota$. -->


<!-- 4. Funding is distributed among $p$ users and the passive pool according to: -->
<!-- . , compute new $$(I, t)$$ and . -->   

<!-- 1. If $$ I  \neq 0$$, then $$I$$ and update block (or oracle fetch number) are saved as attributes to market. -->

<!-- 2. f -->




<!-- partially the pool. Their position triggers the -->
<!-- Case 2: -->

<!-- No positions or transactions are made. The positions are "virtual" in the sense that by investing in the pool, the investors are agreeing to balance all open markets. -->

<!-- ### Liquidation -->

<!-- The risk is that , thus caps can be set -->  

<!-- The rebalancings -->

<!-- ### Example -->

<!-- Overlay has 1k active markets. Each of them are slightly unbalanced to the long side, but not enough for funding to pay for the fees to get in and out of the balancing positions. -->  

<!-- Overlay has 1 market that is *never* balanced. For whatever reason, nobody ever takes the other side. -->
=======
note: 13
oip-num: 1
title: No-Arbitrage Imbalance
status: WIP
author: Michael Feldman (@mikeyrf)
discussions-to: oip-1
created: 2022-05-19
updated: N/A
---

This note aims to address the following issues:

- What is the open interest imbalance in the no-arbitrage limit?
- What is the exposure the protocol assumes in the no-arbitrage limit?


## Summary

The open interest imbalance we should expect to approach in the no-arbitrage limit is

\\[ \frac{\mathrm{OI}\_{imb}}{\mathrm{OI}\_{tot}} = \frac{\Delta r}{2k} \\]

where \\( \Delta r \\) is the difference in "risk-free" rates between the quote
and base currencies for the market. \\( k \\) is our funding governance parameter.

"Risk-free" rates for each respective currency are likely to be the native staking yields, given
covered and uncovered interest rate parity arguments. See [this series](https://nopeitslily.substack.com/p/risk-frees-and-currencies-part-three?utm_source=%2Fprofile%2F26558147-lily-francus&utm_medium=reader2&s=r) by Lily Francus for more detail.

The exposure the protocol is liable for in the no-arbitrage limit is near zero given the funding "burn" mechanism -- the protocol is paid in full for the risk assumed. To achieve this level of stability, however, governors should ensure \\( k \\) satisfies

\\[ \Delta r \ll 2k \\]

This condition results in concavity of the profit liability function \\( \mathrm{PnL}\_{liability}(\tau) \\) (i.e. printing risk protocol takes on) in the no-arbitrage limit.


## Risk-Neutral Imbalance Level

From Equations (29)-(31) of the [V1 Core whitepaper](https://planckcat.mypinata.cloud/ipfs/QmVMX7DH8Kh22kxMyDFGUJcw1a3irNPvyZBtAogkyJYJEv), funding is given by

\\[ f(I) = 2k \cdot I \\]

where

\\[ I(\tau) \equiv \frac{\mathrm{OI}\_{imb}(\tau)}{\mathrm{OI}\_{tot}(\tau)} \\]

\\( f(I) > 0 \\) implies longs pay shorts and the opposite for \\( f(I) < 0 \\).

[Covered interest rate parity](https://en.wikipedia.org/wiki/Interest_rate_parity#Covered_interest_rate_parity) implies the expected funding rate paid by the longs to the shorts in the no-arbitrage limit \\( f(I) = f_Q \\) will be

\\[ f_Q = r_{quote} - r_{base} = \Delta r \\]

the difference in "risk-free" rates between the quote and base currencies of the inverse market. In practice, the "risk-free" rate for OVL should be the yield on the single-sided staking liquidity mining pool (Overlay's version of T-notes). Similarly for ETH, the "risk-free" rate should be the yield from ETH 2 staking.

The risk-neutral open interest imbalance \\( I(\tau) = I\_{Q} \\) would then be

\\[ I\_{Q} = \frac{\Delta r}{2k} \\]


## PnL Liability

From Equation (32) of the V1 Core WP, the protocol is liable for

\\[ \mathrm{PnL}\_{liability}(\tau) = -\mathrm{OI}\_{b_r}(\tau) \cdot P(0) + \mathrm{OI}\_{imb}(\tau) \cdot [P(\tau) - P(0)] \\]

at a time \\( t=\tau \\) in the future. \\( t = 0 \\) is now. \\( \mathrm{OI}\_{imb} \\) is the open interest imbalance over time. \\( \mathrm{OI}\_{b_r} \\) is the open interest removed from the system given the protocol's exposure to the market due to the imbalance.

The profit liability is the amount of OVL the protocol has to print given the initial open interest imbalance at the current time.

Note that

$$\begin{eqnarray}
\mathrm{OI}_{imb}(\tau) &=& \mathrm{OI}_{imb}(0) \cdot e^{-2k\tau} \\
\mathrm{OI}_{b_r}(\tau) &=& \mathrm{OI}_{tot}(0) \cdot \bigg[ 1 - \sqrt{1 - I(0)^2 \cdot ( 1 - e^{-4k\tau})} \bigg]
\end{eqnarray}$$

To simplify the math for the purposes of this note, take the spot price to be driven by a Wiener process

\\[ \frac{P(\tau)}{P(0)} = e^{(\mu - \frac{\sigma^2}{2}) \tau + \sigma W_{\tau}} \\]

with drift \\( \mu \\) and volatility \\( \sigma \\). Then, the expected value is given by

\\[ \mathbb{E}_Q\bigg[ \frac{P(\tau)}{P(0)} \bigg] = e^{\Delta r \cdot \tau} \\]

under the risk-neutral measure \\( Q \\).

### General

Graph of PnL liability *not* necessarily assuming no-arbitrage imbalance level at \\( \tau=0 \\).

<iframe src="https://www.desmos.com/calculator/74d0jtfuw4?embed" width="500" height="500" style="border: 1px solid #ccc" frameborder=0></iframe>


### No-Arbitrage

Graph of PnL liability assuming no-arbitrage imbalance level at \\( \tau=0 \\).

<iframe src="https://www.desmos.com/calculator/vl0yo9m7u0?embed" width="500" height="500" style="border: 1px solid #ccc" frameborder=0></iframe>


## Stability

The system appears very stable in the no-arbitrage limit when \\( \Delta r \ll 2k \\). Stable in the sense of inflation of currency supply is nominal given the profit liability charts above.

The system appears to potentially become unstable when \\( \mu \geq 2k \\) and no-arbitrage breaks down. Additional circuit breaker and cap mechanisms we have limit the damage to these types of events.

To verify stability, one can look at the first and second derivative of the expected value under the risk-neutral measure of the profit liability with respect to time in the limit as \\( t \to 0 \\)

$$\begin{eqnarray}
\lim_{\tau \to 0} \frac{d}{d\tau} \mathbb{E}_Q\bigg[\mathrm{PnL}_{liability}(\tau)\bigg] &=& P(0) \cdot \mathrm{OI}_{imb}(0) \cdot \bigg( \Delta r - f_Q \bigg) = 0 \\
\lim_{\tau \to 0} \frac{d^2}{d\tau^2} \mathbb{E}_Q\bigg[\mathrm{PnL}_{liability}(\tau)\bigg] &=& P(0) \cdot \mathrm{OI}_{imb}(0) \cdot \Delta r \cdot \bigg( \Delta r - 2k \bigg)
\end{eqnarray}$$

This imposes a condition on our governance chosen value for \\( k \\) in order to achieve a concave liability function in time i.e. \\( \lim_{\tau \to 0} \frac{d^2}{d\tau^2} \mathbb{E}\_Q\bigg[\mathrm{PnL}_{liability}(\tau)\bigg] < 0 \\):

\\[ \Delta r < 2k \\]

Fortunately, we calibrate \\( k \\) using VaR at 95, 99% levels, which will produce \\( \Delta r \ll 2k \\). As long as this condition holds, the system should be stable.

Governance will need to monitor \\( \Delta r \\) vs \\( 2k \\) continuously and adjust \\( k \\) accordingly in the event the spread in "risk-free" rates between OVL and e.g. ETH increases significantly. Potentially in V2, \\( k \\) could be adjusted dynamically based on current staking rates in a manipulation-resistant way.
