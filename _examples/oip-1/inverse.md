# numbers

Example. I want to trade the ETH-OVL market on Overlay (inverse). Say I start with 100 OVL to trade.

Assume at the start:

 - 1 OVL = 1 ETH
 - 100 OVL of collateral = 100 ETH of collateral


### Portfolio A: "Synthetic ETH"

I enter into one position:

 - Take out a 1x long position on the ETH-OVL feed on Overlay

What happens in the following two scenarios:

 1. Price of ETH-OVL goes down 25% from 1 OVL / 1 ETH to 0.75 OVL / 1 ETH (i.e. OVL becomes more valuable)
 2. Price of ETH-OVL goes up 25% from 1 OVL / 1 ETH to 1.25 OVL / 1 ETH (i.e. OVL becomes less valuable)

#### Scenario 1: ETH-OVL feed drops 25%

I want to convert back to OVL since for this portfolio I like to denominate in ETH. Price of ETH-OVL has changed to 1 ETH = 0.75 OVL.

1. I exit the 1x long contract. I receive:

- 100 OVL * ( 1 + (0.75 - 1.00) / 1.00 ) = **75 OVL**

2. I swap the spot OVL back for ETH. I receive:

- 75 OVL => 75 OVL / (0.75 OVL/ETH) = **100 ETH**

3. Total I *receive* back:

- **75 OVL** or **100 ETH**

4. For a *profit* of

- **-25 OVL** in OVL terms
- **0 ETH** in ETH terms


#### Scenario 2: ETH-OVL feed increases 25%

I want to convert back to OVL since for this portfolio I like to denominate in ETH. Price of ETH-OVL has changed to 1 ETH = 1.25 OVL.

1. I exit the 1x long contract. I receive:

- 100 OVL * ( 1 + (1.25 - 1.00) / 1.00 ) = **125 OVL**

2. I swap the spot OVL back for ETH. I receive:

- 125 OVL => 125 OVL / (1.25 OVL/ETH) = **100 ETH**

3. Total I *receive* back:

- **125 OVL** or **100 ETH**

4. For a *profit* of

- **+25 OVL** in OVL terms
- **0 ETH** in ETH terms

Notice, in both scenarios, I have a made zero profit ***in ETH terms***, which is what I prefer to denominate in (assume). Not true in OVL terms though.

Thus, this portfolio is effectively "synthetic ETH".


### Portfolio B: "Synthetic OVL"

I split my portfolio into two:

- Swap 50 OVL for 50 ETH on the spot market
- Take out a 1x short position on the ETH-OVL feed on Overlay

What happens in the following two scenarios:

1. Price of ETH-OVL goes down 25% from 1 OVL / 1 ETH to 0.75 OVL / 1 ETH (i.e. OVL becomes more valuable)
2. Price of ETH-OVL goes up 25% from 1 OVL / 1 ETH to 1.25 OVL / 1 ETH (i.e. OVL becomes less valuable)

#### Scenario 1: ETH-OVL feed drops 25%

I want to convert back to OVL since I like to denominate in OVL. Price of ETH-OVL has changed to 1 ETH = 0.75 OVL.

1. I swap the spot ETH back for OVL. I receive:

- 50 ETH => 50 * (0.75 OVL/ETH) = **37.5 OVL**

2. I exit the 1x short contract. I receive:

- 50 OVL * ( 1 - (0.75 - 1.00) / 1.00 ) = **62.5 OVL**

3. Total I *receive* back:

- **100 OVL** or **133.333 ETH**

4. For a *profit* of

- **0 OVL** in OVL terms
- **33.333 ETH** in ETH terms


#### Scenario 2: ETH-OVL feed increases 25%

I want to convert back to OVL since I like to denominate in OVL. Price of ETH-OVL has changed to 1 ETH = 1.25 OVL.

1. I swap the spot ETH back for OVL. I receive:

- 50 ETH => 50 * (1.25 OVL/ETH) = **62.5 OVL**

2. I exit the 1x short contract. I receive:

- 50 OVL * ( 1 - (1.25 - 1.00) / 1.00 ) = **37.5 OVL**

3. Total I *receive* back:

- **100 OVL** or **80 ETH**

4. For a *profit* of

- **0 OVL** in OVL terms
- **-20 ETH** in ETH terms

Notice, in both scenarios, I have a made zero profit ***in OVL terms***, which is what I prefer to denominate in (assume). Not true in ETH terms though.

Thus, this portfolio is effectively "synthetic OVL".
