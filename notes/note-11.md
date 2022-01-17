---
note: 11
oip-num: 1
title: Funding Revisited
status: WIP
author: Michael Feldman (@mikeyrf)
discussions-to: oip-1
created: 2021-01-16
updated: N/A
---

This note aims to address the following issues with [funding](note-4) raised by Mikhail:

- How should we think about our [market exposure](https://hackmd.io/@abdk/ry_09yFut) for risk estimation purposes? And what quantity (associated with market exposure) are we looking to minimize over time through funding?

- When an imbalance exists between longs and shorts, the protocol takes market risk [without being compensated for the risk](https://hackmd.io/@abdk/HydvIc4FY). How can we rethink funding such that the protocol is "compensated" for the imbalance risk it assumes by burning a portion of the funding payment?


## Market Exposure

### Context

One can understand the first issue issue raised through the following example.

Assume there are two traders. Both initially enter the market at the same time \\( t_0 \\) with the same position size in OVL terms \\( \mathrm{OI}\_{l} = \mathrm{OI}\_{s} = \mathrm{OI} \\) and same entry price \\( P_0 \\). Their positions perfectly balance each other, as the PnL exposure the protocol assumes on each side is

\\[ \mathrm{PnL}\_{l}\|\_{t_0 \leq t \leq t_1} = \mathrm{OI} \cdot \bigg[ \frac{P_t}{P_0} - 1 \bigg] \\]
\\[ \mathrm{PnL}\_{s}\|\_{t_0 \leq t \leq t_1} = \mathrm{OI} \cdot \bigg[ 1- \frac{P_t}{P_0} \bigg] \\]

such that the total exposure is zero: \\( \mathrm{PnL}\|\_{t_0 \leq t \leq t_1} = \mathrm{PnL}\_{l} + \mathrm{PnL}\_{s} = 0 \\).

The long trader then exits their position at \\( t_1 \\) while the short remains. The protocol realizes the long PnL through a mint or a burn. Another trader then enters a long position with the same open interest as the last to rebalance the position size on the market, but with a different entry price \\( P_1 \\). Including the realized profits, PnL exposure after \\( t_1 \\) becomes

\\[ \mathrm{PnL}\_{l}\|\_{t \geq t_1} = \mathrm{OI} \cdot \bigg[ \frac{P_1}{P_0} - 1 \bigg] + \mathrm{OI} \cdot \bigg[ \frac{P_t}{P_1} - 1 \bigg] \\]
\\[ \mathrm{PnL}\_{s}\|\_{t \geq t_1} = \mathrm{OI} \cdot \bigg[ 1- \frac{P_t}{P_0} \bigg] \\]

such that the total exposure the protocol assumes is: \\( \mathrm{PnL}\|\_{t \geq t_1} = \mathrm{PnL}\_{l} + \mathrm{PnL}\_{s} = \mathrm{OI} \cdot [\frac{P_1}{P_0} - 1 + \frac{P_t}{P_1} \cdot (1 - \frac{P_1}{P_0})] \\).

This is non-zero even though another trader immediately re-enters on the long side at \\( t_1 \\) to rebalance the position size (notional in OVL terms) on the market. This is due to the difference in entry prices between positions built at \\( t_0 \\) versus the one built at \\( t_1 \\).

If we use funding to incentivize notional position size in OVL terms be balanced between longs and shorts on a market, the protocol will continuously accumulate exposure due to the difference in entry prices for each trade.


### Proposed Solution

If we instead incentivize balance in the "number of contracts" on each side, we eliminate the issue. Assuming OVL collateral \\( N \\) staked to back a position with initial leverage \\( L \\) and entry price \\( P_0 \\), redefine open interest to be the number of contracts on a side (vs the position size in OVL terms) such that

- Position size in OVL terms (notional): \\( Q = N \cdot L \\)
- Open interest (number of contracts): \\( \mathrm{OI} = \frac{Q}{P_0} \\)
- PnL of the position: \\( \mathrm{PnL} = \pm \mathrm{OI} \cdot [P_t - P_0] \\)

Returning to the prior example, PnL exposure after both traders enter at \\( t_0 \\) with the same position size \\( Q_0 \\) and number of contracts \\( \mathrm{OI} = \frac{Q_0}{P_0} \\) is

\\[ \mathrm{PnL}\_{l}\|\_{t_0 \leq t \leq t_1} = \mathrm{OI} \cdot \bigg[ P_t - P_0 \bigg] \\]
\\[ \mathrm{PnL}\_{s}\|\_{t_0 \leq t \leq t_1} = \mathrm{OI} \cdot \bigg[ P_0 - P_t \bigg] \\]

such that total exposure before the unwind is still zero: \\( \mathrm{PnL}\|\_{t_0 \leq t \leq t_1} = \mathrm{PnL}\_{l} + \mathrm{PnL}\_{s} = 0 \\).

At \\( t_1 \\), the long exits and re-enters again with the same *number of contracts*, but this time with different position size \\( Q_1 = \mathrm{OI} \cdot P_1 \\) in OVL terms. Including the realized profits, PnL exposure after \\( t_1 \\) becomes

\\[ \mathrm{PnL}\_{l}\|\_{t \geq t_1} = \mathrm{OI} \cdot \bigg[ P_1 - P_0 \bigg] + \mathrm{OI} \cdot \bigg[ P_t - P_1 \bigg] \\]
\\[ \mathrm{PnL}\_{s}\|\_{t \geq t_1} = \mathrm{OI} \cdot \bigg[ P_0 - P_t \bigg] \\]

such that the total exposure the protocol assumes remains zero: \\( \mathrm{PnL}\|\_{t \geq t_1} = \mathrm{PnL}\_{l} + \mathrm{PnL}\_{s} = 0 \\).

If we use funding to incentivize number of contracts be balanced between longs and shorts on a market (instead of notional), we solve the issue with differing entry prices.


### Imbalance in Number of Contracts

What is the exposure the protocol now assumes when the number of contracts remain unbalanced for a period of time?

Instead of the long trader exiting all of their contracts like in the prior example, assume they exit a portion \\( a \cdot \mathrm{OI} \\) of their contracts at \\( t_1 \\) and re-enter with another \\( a \cdot \mathrm{OI} \\) contracts at a later time \\( t_2 \\). The open interest (number of contracts) is \\( (1-a) \cdot \mathrm{OI} \\) on the long side and \\( \mathrm{OI} \\) on the short side from \\( t_1 \leq t \leq t_2 \\).

PnL exposure after \\( t_2 \\) becomes

\\[ \mathrm{PnL}\_{l}\|\_{t \geq t_2} = a \cdot \mathrm{OI} \cdot \bigg[ P_1 - P_0 \bigg] + a \cdot \mathrm{OI} \cdot \bigg[ P_t - P_2 \bigg] + (1-a) \cdot \mathrm{OI} \cdot \bigg[ P_t - P_0 \bigg] \\]
\\[ \mathrm{PnL}\_{s}\|\_{t \geq t_2} = \mathrm{OI} \cdot \bigg[ P_0 - P_t \bigg] \\]

such that the total exposure the protocol assumes is the price exposure on the contract imbalance from \\( t_1 \leq t \leq t_2 \\): \\( \mathrm{PnL}\|\_{t \geq t_2} = \mathrm{PnL}\_{l} + \mathrm{PnL}\_{s} = a \cdot \mathrm{OI} \cdot [ P_1 - P_2 ] \\).

The protocol should aim to have the contract imbalance \\( \mathrm{OI}\_{imb} = \mathrm{OI}\_{l} - \mathrm{OI}\_{s} = - a \cdot \mathrm{OI} \\) from \\( t_1 \leq t \leq t_2 \\) decay toward zero through funding payments.

## Funding Burns
