---
note: 3
oip-num: 1
title: Hedging OVL Exposure
status: WIP
author: Michael Feldman (@mikeyrf)
discussions-to: oip-1
created: 2021-03-02
updated: N/A
---

Major issue to address with this note:

- How do I hedge out my OVL price exposure when entering into a position on an Overlay market?


## Context

In order to take positions on markets offered by the protocol, traders need to stake the settlement currency of the system (OVL). For traders that don't want price exposure to OVL but still wish to take a position on a market, they should be able to construct a portfolio that hedges out OVL price risk with respect to a quote currency like ETH. I'll address how to construct this combination of positions in this note.

<!-- TODO: For context, ... need to talk about offering OVL-ETH feed after bootstrap phase -->
