# numbers

Example. I want to trade the X market on Overlay but hedge out some OVL price exposure through the ETH-OVL market (inverse). Say I start with 100 OVL to trade.

Assume at the start:

 - 1 OVL = 1 ETH
 - 100 OVL of collateral = 100 ETH of collateral
 - q = 0.8


## Portfolio A: 1x long on X

I enter into two positions:

 - Take out a 1x long position on X feed using 80 OVL
 - Take out a long position on the ETH-OVL feed with l = 1/(1-q) = 5x leverage using 20 OVL

What happens in the following two scenarios:

 1. Price of X goes up 10% but ETH-OVL goes up 5% from 1 OVL / 1 ETH to 1.05 OVL / 1 ETH (i.e. OVL becomes less valuable)
 2. Price of X goes up 20% but ETH-OVL goes up 25% from 1 OVL / 1 ETH to 1.25 OVL / 1 ETH (i.e. OVL becomes less valuable)

Comparing hedged with unhedged.

### Case 1: X increases 10%, EO increases 5%

#### Unhedged X Position

Value of the unhedged long at exit in

 - OVL terms: 100 OVL * (1 + 0.1) = 110 OVL
 - ETH terms: 110 OVL / (1.05 OVL / ETH) = 104.76 ETH

for a profit of 104.76 ETH - 100 ETH = 4.76 ETH. The 10% gain from the X feed position has been reduced to a 4.76% gain in ETH terms.

#### Hedged X Position

Value of the hedged long at exit in

 - OVL terms: 80 OVL * (1 + 0.1) + 20 OVL * (1 + 5 * 0.05) = 113 OVL
 - ETH terms: 113 OVL / (1.05 OVL / ETH) = 107.62 ETH

for a profit of 107.62 ETH - 100 ETH = 7.62 ETH. The 10% gain from the X feed position has been reduced to a gain of 7.62% in ETH terms.

Hedged portfolio protects the gains in ETH terms.

##### Check Hedged PnL Formula

 - ETH terms: PnL = (0.8 * 100 OVL / (1.05 OVL / ETH)) * 1 * 0.1 = 7.62 ETH

Checks out.


### Case 2: X increases 20%, EO increases 25%

#### Unhedged X Position

Value of the unhedged long at exit in

 - OVL terms: 100 OVL * (1 + 0.2) = 120 OVL
 - ETH terms: 120 OVL / (1.25 OVL / ETH) = 96 ETH

for a profit of 96 ETH - 100 ETH = -4 ETH. The 20% gain from the X feed position has been reduced to a loss of 4% in ETH terms.

#### Hedged X Position

Value of the hedged long at exit in

 - OVL terms: 80 OVL * (1 + 0.2) + 20 OVL * (1 + 5 * 0.25) = 141 OVL
 - ETH terms: 141 OVL / (1.25 OVL / ETH) = 112.8 ETH

for a profit of 112.8 ETH - 100 ETH = 12.8 ETH. The 20% gain from the X feed position has been reduced to a gain of 12.8% in ETH terms.

Hedged portfolio protects the gains in ETH terms even more significantly.

##### Check Hedged PnL Formula

 - ETH terms: PnL = (0.8 * 100 OVL / (1.25 OVL / ETH)) * 1 * 0.2 = 12.8 ETH

Checks out.


## Portfolio B: 2x short on X

I enter into two positions:

 - Take out a 2x short position on X feed using 80 OVL
 - Take out a long position on the ETH-OVL feed with l = 1/(1-q) = 5x leverage using 20 OVL

What happens in the following two scenarios:

 1. Price of X goes up 10% but ETH-OVL goes up 5% from 1 OVL / 1 ETH to 1.05 OVL / 1 ETH (i.e. OVL becomes less valuable)
 2. Price of X goes up 20% but ETH-OVL goes up 25% from 1 OVL / 1 ETH to 1.25 OVL / 1 ETH (i.e. OVL becomes less valuable)

Comparing hedged with unhedged. Ignore potential liquidations.

### Case 1: X increases 10%, EO increases 5%

#### Unhedged X Position

Value of the unhedged 2x short at exit in

 - OVL terms: 100 OVL * (1 - 2 * 0.1) = 80 OVL
 - ETH terms: 80 OVL / (1.05 OVL / ETH) = 76.19 ETH

for a profit of 76.19 ETH - 100 ETH = -23.81 ETH. The 20% loss from the X feed position has worsened to a 23.81% loss in ETH terms.

#### Hedged X Position

Value of the hedged 2x short at exit in

 - OVL terms: 80 OVL * (1 - 2 * 0.1) + 20 OVL * (1 + 5 * 0.05) = 89 OVL
 - ETH terms: 89 OVL / (1.05 OVL / ETH) = 84.76 ETH

for a profit of 84.76 ETH - 100 ETH = -15.24 ETH. The 20% loss from the X feed position has been reduced to a -15.24% loss in ETH terms.

Hedged portfolio reduces the losses in ETH terms.

##### Check Hedged PnL Formula

 - ETH terms: PnL = (0.8 * 100 OVL / (1.05 OVL / ETH)) * (-2 * 0.1) = -15.24 ETH

Checks out.


### Case 2: X increases 20%, EO increases 25%

#### Unhedged X Position

Value of the unhedged long at exit in

 - OVL terms: 100 OVL * (1 - 2 * 0.2) = 60 OVL
 - ETH terms: 60 OVL / (1.25 OVL / ETH) = 48 ETH

for a profit of 48 ETH - 100 ETH = -52 ETH. The 40% loss from the X feed position has worsened to a 52% loss in ETH terms.


#### Hedged X Position

Value of the hedged long at exit in

 - OVL terms: 80 OVL * (1 - 2 * 0.2) + 20 OVL * (1 + 5 * 0.25) = 93 OVL
 - ETH terms: 93 OVL / (1.25 OVL / ETH) = 74.4 ETH

for a profit of 74.4 ETH - 100 ETH = -25.6 ETH. The 40% loss from the X feed position has been reduced to a loss of 25.6% in ETH terms.

Hedged portfolio reduces the losses in ETH terms even more significantly.

##### Check Hedged PnL Formula

 - ETH terms: PnL = (0.8 * 100 OVL / (1.25 OVL / ETH)) * (-2 * 0.2) = -25.6 ETH

Checks out.


## Portfolio C: 3x long on X

I enter into two positions:

 - Take out a 3x long position on X feed using 80 OVL
 - Take out a long position on the ETH-OVL feed with l = 1/(1-q) = 5x leverage using 20 OVL

What happens in the following two scenarios:

 1. Price of X goes up 10% but ETH-OVL goes up 5% from 1 OVL / 1 ETH to 1.05 OVL / 1 ETH (i.e. OVL becomes less valuable)
 2. Price of X goes up 20% but ETH-OVL goes up 25% from 1 OVL / 1 ETH to 1.25 OVL / 1 ETH (i.e. OVL becomes less valuable)

Comparing hedged with unhedged.

### Case 1: X increases 10%, EO increases 5%

#### Unhedged X Position

Value of the unhedged 3x long at exit in

 - OVL terms: 100 OVL * (1 + 3 * 0.1) = 130 OVL
 - ETH terms: 130 OVL / (1.05 OVL / ETH) = 123.81 ETH

for a profit of 123.81 ETH - 100 ETH = 23.81 ETH. The 30% gain from the X feed position has been reduced to a 23.81% gain in ETH terms.

#### Hedged X Position

Value of the hedged long at exit in

 - OVL terms: 80 OVL * (1 + 3 * 0.1) + 20 OVL * (1 + 5 * 0.05) = 129 OVL
 - ETH terms: 129 OVL / (1.05 OVL / ETH) = 122.86 ETH

for a profit of 122.86 ETH - 100 ETH = 22.86 ETH. The 30% gain from the X feed position has been reduced to a gain of 22.86% in ETH terms.

Hedged portfolio reduces the gains in ETH terms due to the 20 OVL of capital taken away from the leverage on the 3x long to create the hedge.

##### Check Hedged PnL Formula

 - ETH terms: PnL = (0.8 * 100 OVL / (1.05 OVL / ETH)) * 3 * 0.1 = 22.86 ETH

Checks out.


### Case 2: X increases 20%, EO increases 25%

#### Unhedged X Position

Value of the unhedged long at exit in

 - OVL terms: 100 OVL * (1 + 3 * 0.2) = 160 OVL
 - ETH terms: 160 OVL / (1.25 OVL / ETH) = 128 ETH

for a profit of 128 ETH - 100 ETH = 28 ETH. The 60% gain from the X feed position has been reduced to a gain of 28% in ETH terms.

#### Hedged X Position

Value of the hedged long at exit in

 - OVL terms: 80 OVL * (1 + 3 * 0.2) + 20 OVL * (1 + 5 * 0.25) = 173 OVL
 - ETH terms: 173 OVL / (1.25 OVL / ETH) = 138.4 ETH

for a profit of 138.4 ETH - 100 ETH = 38.4 ETH. The 60% gain from the X feed position has been reduced to a gain of 38.4% in ETH terms.

Hedged portfolio protects the gains in ETH terms.

##### Check Hedged PnL Formula

 - ETH terms: PnL = (0.8 * 100 OVL / (1.25 OVL / ETH)) * 3 * 0.2 = 38.4 ETH

Checks out.
