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



1. The funding mechanism as outlined in [OIP1](note-1) can only ever *damp* the risk to the system, never eliminate it. 
	1. Investors are incentivized to make their balancing positions as small as possible. 
	2. If we enforce a minimum size to a position to collect funding, it must always be much less than the imbalance.

2. The current mechanism design leads to undesirable side-effects. 
	1. Balancing positions must occur in the last moment before oracle fetch.
	2. It is not possible to know the imbalance exactly without knowing which transactions in the  mempool will  be mined in the same block as an oracle fetch. 
	3. Last-minute competition can lead to 'overshoot', where investors tip the imbalance to the other side and pay funding.
	4. Parasitic capital can gather funding without reducing risk to the system (this will be the main use of the mechanism).

3. Collecting funding is a specialized activity. 
	1. To remain profitable, investors must remain nimble, reacting quickly to changes in the imbalance. 
	2. Investors must keep track of an increasing number of markets.

4. Collecting funding is expensive.
	1. A funding round trip using ETH or DAI involves buying OVL, locking OVL, unlocking OVL, and selling OVL. This means paying gas *and* trading fees 4 times each. 
	2. Any automation of funding strategies (as in the case of mOVL, mDAI, mETH)  will generate front-running strategies.

5. The current mechanism has negative feedback that limits its size.
	1. By 3.1 and 4.1, investors must be nimble to make yield, but this means HFT, which decreases yield through fees. 
	2. The greater number of active investors, the more fee competition and overshoot, reducing investors. 
	3. By 3.2, the more the system scales, the greater the technical debt for investors, limiting investors. 
	4. Problem 4.2 insures that the larger funding becomes, the more front-running, the smaller it becomes. 





<!-- 4. The stragegy that has investors gaining yield on OVL on the OVL-ETH feed requires them to first sell half their OVL for spot ETH. This becomes increasingly difficult as Overlay scales to many assets across multiple exchanges, and  it is impossible for non-financial markets such as pure scalar data feeds (e.g. the CPI). -->

<!-- tokenized position -->

<!-- pThese are effectively tokenized basis positions that users can easily swap into or out of on spot AMMs as funding rates go against their respective side or provide liquidity for on spot exchanges specializing in like-asset pairs (e.g. Magic ETH & ETH pool). -->


Problem 1.1 entails that OI caps in one direction could be hit while prices move rapidly. The OVL supply would  then  inflate significantly. Thus, in extreme cases, the funding mechanism does not fulfil its primary purpose.  

The issues collectively seem significant.  Because the effectiveness of the funding mechanism is  a bottleneck for the system itself, unless these issues can be solved the system cannot scale. 

Fortunately, all but one of the above issues can be solved at one time, by distinguishing between positionrs and investors. Before presenting the solution, however, we show why we *must* distinguish between them.


<!-- , by slightly altering the specification of the magic contracts. --> 

<!-- These issues collectively assure that 1) the balancing mechanism will be a specialized activity, requiring ongoing maintenance and incurring technical debt, and yields will not be as good as they might be, thus limiting the appeal, and  2) the magic contracts as currently imagined do not escape issues 1-6 above, and because of issue 7 actually increase the risk to the system. --> 



<!-- To allow for an Overlay-managed pool, similar to a Yearn vault, which incurs zero transactions fees, takes the opposite side of the imbalance on *all* Overlay markets collectively, and allows for yield on both OVL and ETH. -->



#### Parasitic Capital
Problem 2.4 makes it imperative to distinguish between positionrs and investors. To get the basic idea across, pretend for a moment that there are *two* positionrs on DAI-OVL. One has gone long with size $$n$$, and the other has gone long *and* short, both with size $$N>n$$. The imbalance is $$n$$, and after one funding period the longs must pay $$kn$$, which goes to the short side. In that time, say DAI-OVL rose by $$r$$ percent. To update PnL, there will be two `mint` and one `burn` calls to the market contract, plus whatever calls are made to effect funding transfers.  The first positionr has 
\\[n\Big(1 +r - kn\frac{n}{n+N}\Big)\\]
while the second positionr  has
\\[N\Big(1 +r - kn\frac{N}{n+N}\Big) + N(1 - r + kn) = 2N + kn\frac{n}{n+N}\\]

This shows that funding can be collected passively without being nimble or even worrying about trading, by simply taking the long and short side in equal parts. This is a weakness of the current funding mechanism since it represents parasitic capital. There is every reason to think that a significant amount  of OI will  be given over to this type of position. 

## Passive Balancing Pools


Funding must flow from OI on the market contract to OI on a different type of contract, to which investors which balance positionr OI will deposit. What should the investor contract  look like? 



It is clear that we cannot have passive pools of locked OVL tracking the value of OVL, DAI, or ETH, because this simply shifts the inflation problem to the investor pools. Since these pools are likely to be large, the problem would be worse. Thus, we need pools of unlocked OVL, along with pools of  DAI and ETH (and WBTC and any other base currency we care to list). 


In fact, the idea of magic tokens is almost the same as a passive balancing pool.  The way the magic contracts would work as proposed in [OIP-1](note-1) would be to automate the swaps and Overlay calls required to enter balancing positions. It is clear that these swaps must be entered and exited opportunistically, each funding period. The majority of the magic pools would be passively sitting, denominated in OVL, ETH, and DAI, while a small amount of it would be deployed at any time to balance positionr OI. 

If the funding mechanism is implemented as currently specified, the magic tokens are subject to all the problems above. However, since a distinction between positionrs and investors is forced on us, we may treat the investors differently than the positionrs. This represents no system risk since all investor positions are automated by our contracts. 

If the Overlay system allowed the magic contracts to make swaps *immediately after* an oracle fetch and receive the *last* price (rather than the next one, as positionrs using the market contract would receive), then the imbalance could be eliminated entirely. More precisely, the logic would be:

1. Users taking positions using the market contract generate an imbalance $$I$$ after the oracle fetch at $$t_0$$, getting price $$P_0$$.

2. On block $$t_0 + 1$$, the magic contract makes the required swaps on an AMM. If $$I>0$$ then ETH or DAI is sold for $$I$$ worth of OVL.  Otherwise $$I$$ OVL is sold for ETH or DAI. The price $$P_0$$ is saved and associated with this swap. 

3. Whenever a positionr unwinds at price $$P(t)$$, the return $$nr$$ to this positionr is not generated from a `mint` or `burn` call, but a `transfer` call, either from the $$I$$ OVL held by the magic contract, or to it. 

4. The magic contracts exit their positions gradually as imbalance changes, or all at once as it changes sign.  


### Discussion
The funding mechanism has promise but requires significant tuning to fulfil its purpose. The main problems are 1.1 (imbalance can never go to zero), 2.4 (parasitic capital) and all problems 5 (the mechanism is beset with negative feedback). 


All of these problems are bugs resulting from the failure to separate positionrs and investors. Once this separation is forced on us (which it is), it is clear that *all* funding must flow  from positionrs to investors. This will probably require the funding rate to be lower, since positionrs are never collecting funding. The $$k$$ constant can be tuned depending on positionr and investor behavior (rather than, or in addition to, the current factors involved in tuning). 

Luckily, separating positionrs and investors allows us to resolve problems 1, 2, 3, and 5, and all their subproblems.  One of the most significant results of this mechanism is that problem 1.1 is resolved. The risk to the Overlay system on markets balanced by investors is zero. This solves the inflation problem completely. 

Another very significant result is that the negative feedback of problem 5 becomes positive feedback. Investors do not need to be nimble to make yield, resulting in fewer fees and thus higher yield. There is no fee competition or overshoot. The more the system scales, the larger the yield opportunity with the *same* level of technical debt. Most significantly, it is clear that the OI caps for the positionrs should be identified with the depth of the passive pools. Since these pools are likely to be large, the positionr caps can be large, increasing volume, and thus increasing yield, and thus increasing pool depth in a positive feedback loop. 

<!-- (Payout OI should be a function of OVL-ETH and OVL-DAI liquidity on AMMs) -->

The last problem (#4) involves the expense of making four positions to collect funding, along with the concomitant front-running into and out of OVL on an AMM that is sure to emerge. This may be unavoidable. In any case we leave it to a future discussion. 

<!-- How can we resolve this? -->

<!-- There are different types of solution. --> 

<!-- 1. Force all investors to deposit certain proportions of OVL, ETH and DAI, creating some  impermanent loss risk. --> 

<!-- 2. Allow automated lending between the pools, creating some price exposure risk. --> 








<!-- [OIP-1](note-1) presented the idea of a contract which facilitates the required balancing positions, returning an ERC-20 token such as meth or mOVL (Magic ETH and Magic OVL).  mentioned the possibility of users swapping 'into or out of on spot AMMs' or providing liquidity for 'exchanges specializing in like-asset pairs'. The solution to the above funding problems is evident by focusing on the special nature of the  mOVL pool. -->
<!-- <!-1- However for there to be a large amount of outstanding mETH or mOVL, as currently specified, those positions would have to be placed on the relevant market, implying that 1) the caps on these markets will have to be made very large to accomodate 'balancing' liquidity and 2) the 'balancing' liquidity is no longer balancing but sitting there passively. -1-> --> 

<!-- Holders of mOVL want yield on OVL without incurring price risk. Each mOVL is focused on a specific pair, e.g. OVL-DAI, OVL-ETH, OVL-WBTC. For simplicity we will identify mOVL in this note with the OVL-DAI pair. The relevant position is able to provide balance on the *long* side of OVL-DAI (buying OVL when most volume is shorting it) only, and it hedges price risk by selling half into DAI on spot. --> 

<!-- An equivalent position purely on the Overlay system would be to short OVL-DAI with half the stack and long it with the other half. Of course then funding cannot be collected because the imabalance is not altered by this position. However, if we make mOVL holders 'first-class citizens' we iare able to solve most of the problems listed above. In fact we can see that many of them are created by a refusal to distinguish between positionrs and investors. -->  

<!-- The basic idea is not to write contracts that enter the relevant positions for a user and issue ERC-20s, but rather which pool OVL liquidity, and then replace `mint` and `burn` calls with built-in `transfer` calls. This solution has positive feedback features which leads to a virtuous cycle, and promises a mature system that  *always* balance all markets. In this end state, *all* inflation risk to the Overlay system is completely eliminated, and scaling becomes a function of the liquidity in mOVL. --> 
<!-- ## Basic Idea of Passive Pools -->
<!-- Because investors have more money and seek yield on huge pools of capital, they will want to go long and short very large. However, OI caps are built for positionrs, and at all times we must assume that the entirety of one side will cancel. Thus the OI caps must be relatively small. The more investors crowd out positionrs, furthermore, the less reason there is for them to do so. --> 

<!-- What we propose here is to distinguish between positionrs and investors. We will have two separate contracts for them. The imbalance is still $$n$$, but now there is only $$n$$ OVL locked, so the first positionr pays *all* of the funding. Under the hood, we --> 
<!-- replaced the two `mint` and one `burn` calls  with one `mint`, one `burn` and one `transfer` call, so that the $$nr$$ OVL won by the first positionr comes from the second positionr's loss. (We still have a burn call because $$N>n$$.) If we can balance the sizes of offsetting positions (roughly, speaking, so $$N = n$$), then we can avoid `mint` and `burn` calls and only use `transfer`. If passive balancing pools can work, the OVL gets transferred around just as in a traditional CEX. --> 

<!-- In this picture, the  first positionr would have -->
<!-- \\[n(1 +r - kn)\\] -->
<!-- while the second positionr would have --> 
<!-- \\[2N + kn.\\] -->


<!-- ### Specific Idea -->

<!-- Ideally, the funding rate mechanism should *insure* that the risk to the system is zero. This is far from the case as it is currently designed. By tweaking the funding mechanism slightly, however, this can be achieved.  From [OIP-1](note-1): -->


<!-- >Let the open interest contributed by any one position to the long (short) side be the number \\(N \\) of OVL locked to that side, times the leverage \\(L\\) associated with those \\(N\\)  OVL. Thus, for positionr \\( j \\) going long (thus the subscript \\(l\\)) we have -->

<!-- >\\[ \mathrm{OI}\_{jl} = L_{jl} \cdot N_{jl}\\] -->


<!-- >The funding payment will probably be computed each oracle fetch rather than each block, as oracle times may vary by market and are a natural 'heartbeat'.  Consequently, let us assume there are \\(m \\) funding payments accrued between \\(t_0\\) and \\(t\\), and that each one takes place at some time \\(t_i\\) for \\(i = 1,2,\ldots,m\\). --> 

<!-- We will slightly alter notation and let \\(I(t) = \mathrm{OI}\_{imb}(t)\\), the imbalance at time $$t$$, and write $$I(t) = L(t) - S(t)$$, long minus short open interest at time $$t$$. -->

<!-- Assume at $$t_0$$ there are no positions and so $$L_0 = S_0 = I_0 = 0$$. Let the next oracle fetch be at \\(t^\* > t_0\\) and say there are $$h$$ blocks between $$t_0$$ and \\(t^\*\\). So according to the subscript notation where $$t_i$$ is the $$i^\mathrm{th}$$ oracle fetch and funding payment, we have \\(t_{0} + h = t_{1} = t^\* \\). --> 

<!-- During these $$h$$ blocks, say there are positions queued on both the long and short side. The sum of all these positions will make up $$I_1 = L_1 - S_1$$. The rational behavior for an investor trying to collect funding as currently designed is to wait until the last moment before $$t_1$$ and enter an offsetting position. (Otherwise, how does the invesor know which side to come in on?) However, others may be doing the same thing and so there will be competition, driving up the gas the investors have to pay, with potential bad effects including 1) overshoot as multiple investors make offsetting positions and wind up *paying* funding next block rather than collecting it, or 2) minimal balancing as investors seek to balance with the smallest possible amount that is still cost effective. --> 

<!-- Say the balancing positions that come in from investors represent $$B$$ open interest. Then we will have $$ \mathrm{abs}(L_1 - S_1) > \mathrm{abs}(L_1 - S_1 \pm B_1)$$, if there is no overshoot. If there is overshoot the sign of $$I_1$$ can be opposite (and abs($$I$$) may even be greater i.e. worse) than it would have been if there were no investors. --> 

<!-- <!-1- The way the funding payments work currently is that one user pays gas to settle *all* positions in the queue as well as funding payments. -1-> --> 
<!-- The brute force way of making funding payments involves looping over each address's position and shrinking or growing it accordingly. If there are $$m$$ longs and $$n$$ shorts, then this is $$mn$$ writes. As the system scales with large caps on popular markets, this becomes too expensive. Another (better) way is to do a single write and save the funding *rate* at each block as a signed int, and then each time a positionr exits a position, read back through the history of funding payments they would have received using the brute force method, and sum them. Of course, if this can be done, we can write nothing, and simply look at the imbalance at each block and compute the funding rate dynamically upon unwind. --> 

<!-- This observation shows that computing balances upon entry and exit of positions *as though* the mechanism operated in real-time is desireable, and of course the more gas-efficient we can make the system generally the better. We should therefore have a bias towards virtualizing any transactions that we can. -->  

<!-- Another important observation is that we can currently not say whether a last-minute position represents an investor or someone taking directional risk. However, the entire idea of funding payments is predicated on a discinction between such 'positionrs' and investors. The latter do not want directional risk and want yield. The funding payments are currently set up to not distinguish between positionrs and investors at all, and this may be desireable. However, it is by no means *a priori* undesirable to make the distinction at the system level. --> 

<!-- ### Details -->
<!-- Let us now assume that we have a pool of mDAI. Depositors into the magic DAI contract will now be identified exclusively with investors, while anyone taking position on DAI-OVL market will be a positionr. Define a constant $$\beta \in (0,1]$$ that will determine how much of the funding goes to positionrs reducing imbalance, and how much goes to investors, who will *eliminate* the remainder. When $$\beta = 1$$ all of the funding goes to the investors. --> 

<!-- For simplicity, assume the scenario above with $$L_0 = 0 = S_0$$, and let $$L_1 \neq 0 = S_1$$, and set $$\beta = 1$$. All the imbalance is on the long side, and no positionrs are shorting. The funding payment for this period over $$h$$ blocks will be $$kL_1$$. Say at the next oracle fetch a positionr exits, whose position is $$.1L_1$$. She pays gas to make four things happen: --> 

<!-- 1. her position is unwound -- this is the standard behavior of the market contract which we need anyway. --> 

<!-- 2. the oracle is updated -- this we also need and are planning to implement. -->  

<!-- 3. funding is paid to mDAI -- this is new, the positionr pays to transfer $$.1kL_1$$ from her own OVL balance to mDAI. --> 

<!-- 4. the mDAI pool shrinks/grows -- this is new, it is *as though* the mDAI pool had entered a short position on DAI-OVL at the last possible moment, with size $$S_1 = L_1$$, perfectly balancing the book. --> 

<!-- The above example can be generalized to any case where $$L_1 > S_1$$. If $$S_1 > L_1$$, then it is mOVL that plays the balancing role. -->  

<!-- Now let us imagine a scenario where $$\beta \neq 1$$, and $$S_1 \neq 0$$, but we still have $$I_1 > 0$$. In this case funding is still paid to mDAI, but some of it goes to the positionrs on the short side as well. It seems reasonable to pay funding to everyone on a pro-rata basis as originally designed. In this case $$\beta$$ would change each oracle fetch, and for the $$m^\mathrm{th}$$ funding payment, can be computed as --> 

<!-- \\[\beta(m) = \pm\frac{I(m)}{G(m)}\\] -->

<!-- where $$G=L$$ if $$L>S$$ and otherwise $$G=S$$, and the sign changes to negative if $$G = S$$. --> 

<!-- Thinking about $$\beta$$ is helpful to determine how we wish to distribute funding payments, and to what degree we want positionrs to benefit from funding payments as well as paying them. It seems desireable that positionrs should receive funding, since it makes them more likely to also pay it. --> 

<!-- ### Conclusions -->
<!-- One interesting feature of this idea is that, because OVL is the settlement currency, mOVL is special in several ways: -->

<!-- 1. A *massive* amount of short pressure will be exerted on ETH-OVL and especially DAI-OVL via hedging, thus creating juicy yields for mOVL holders. -->

<!-- 2. Any new X market that we list is an X-OVL market, which means that the mOVL pool automatically can get yield from positionrs going short there. Thus, the more markets we list, the greater the yield for mOVL, driving capital into mOVL, allowing us to list more markets. -->  

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

<!-- 2. The passive pool is considered to have been trading the market alongside the $p$ positionrs, with size $$\alpha \iota$$. For example, $$\alpha = .33\$$. Compute the "virtual imbalance" -->  
<!-- \\[\\] -->

<!-- If $$\iota \neq 0$$, compute funding payments between $\tau$ and $$t$$. Say $$m$$ oracle fetches have occurred between $$\tau$$ and $$t$$. So the funding is -->
<!-- \\[ F = \iota (1-2k)^m\\] -->

<!-- 3. Distribute $F$ pro rata between the $p$ positionrs as follows. Say $$\sum N_{ai} = P$$. Then we must have $$OI_{\hat{a}} - P = \iota$. -->


<!-- 4. Funding is distributed among $p$ positionrs and the passive pool according to: -->
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
