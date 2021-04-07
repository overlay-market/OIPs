# numbers

Example. I want to trade the OVL-ETH market on Overlay. Say I start with 100 OVL to trade.

Assume at the start:

 - 1 OVL = 1 ETH
 - 100 OVL of collateral

I split my portfolio into two:

 - Swap 50 OVL for 50 ETH on the spot market
 - Take out a 1x long position on the OVL-ETH feed on Overlay

What happens in the following two scenarios:

 1. Price of OVL-ETH goes down 25% from 1 ETH / 1 OVL to 0.75 ETH / 1 OVL
 2. Price of OVL-ETH goes up 25% from 1 ETH / 1 OVL to 1.25 ETH / 1 OVL

#### Scenario 1: OVL-ETH feed drops 25%

I want to convert back to OVL since I like to denominate in OVL. Price of OVL-ETH has changed to 1 OVL = 0.75 ETH.

1. I swap the spot ETH back for OVL. I receive:

- 50 ETH => 50 / (0.75 ETH/OVL) = **66.667 OVL**

2. I exit the 1x long contract. I receive (notice the linear payout on my 50 OVL staked):

- 50 OVL * ( 1 + (0.75 - 1.00) / 1.00 ) = **37.5 OVL**

3. Total I *receive* back:

- **104.167 OVL** or **78.125 ETH**

4. For a *profit* of

- **+4.167 OVL** in OVL terms
- **-21.875 ETH** in ETH terms


#### Scenario 2: OVL-ETH feed increases +25%

I want to convert back to OVL since I like to denominate in OVL. Price of OVL-ETH has changed to 1 OVL = 1.25 ETH.

1. I swap the spot ETH back for OVL. I receive:

- 50 ETH => 50 / (1.25 ETH/OVL) = **40 OVL**

2. I exit the 1x long contract. I receive (notice the linear payout on my 50 OVL staked):

- 50 OVL * ( 1 + (1.25 - 1.00) / 1.00 ) = **62.5 OVL**

3. Total I *receive* back:

- **102.5 OVL** or **128.125 ETH**

4. For a *profit* of

- **+2.5 OVL** in OVL terms
- **+128.125 ETH** in ETH terms


Notice, in both scenarios, I have made profit ***in OVL terms***, which is what I prefer to denominate in (assume). Not true in ETH terms though.
