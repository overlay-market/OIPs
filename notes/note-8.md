---
note: 8
oip-num: 1
title: Bid-Ask Spread
status: WIP
author: Adam Kay (@mcillkay), Michael Feldman (@mikeyrf)
discussions-to: oip-1
created: 2021-08-03
updated: N/A
---

Issue to address with this note:

- Prevent traders from taking advantage of the fact that the TWAP is a lagging indicator of the spot price.


## Context

Offering Uniswap TWAPs as markets on Overlay comes with a catch. The TWAP averaged over the *previous* \\( \Delta \\) blocks only catches up to changes in the spot price *after the next* \\( \Delta \\) blocks have gone by. This is easily exploitable as a trader, particularly on large jumps in spot.

A trader could wait for a jump to happen on the spot market, realize they have \\( \Delta \\) blocks to place the appropriate trade on the Overlay TWAP market, and scalp an easy assured OVL profit, exiting after the next \\( \Delta \\) averaging window passes by. We've already seen this on [Kovan](https://kovan.overlay.exchange/) with our old contracts.
