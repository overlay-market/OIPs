---
oip: 1
title: Monetary Policy and Pricing Model
status: WIP
author: Michael Feldman (@mikeyrf), Michael Nowotny (@michaelnowotny), Adam Kay (@mcillkay)
discussions-to: <Create a new thread on https://gov.overlay.market/ and drop the link here>
created: 2021-01-09
updated: N/A
---

## Simple Summary
<!--"If you can't explain it simply, you don't understand it well enough." Simply describe the outcome the proposed changes intends to achieve. This should be non-technical and accessible to a casual community member.-->
Provides incentives for core supporters of the protocol via pass-through trading fees. Floats the market price for all feeds offered to enable price discovery.

## Abstract
<!--A short (~200 word) description of the proposed change, the abstract should clearly describe the proposed change. This is what *will* be done if the OIP is implemented, not *why* it should be done or *how* it will be done. If the OIP proposes deploying a new contract, write, "we propose to deploy a new contract that will do x".-->
Updates to the monetary policy and pricing model for each Overlay-offered market are suggested to ensure the long-term stability and robustness of the system. Pricing of each trading position entered or exited on a market would be determined by a constant function market maker (CFMM) with periodic minting and burning to track the underlying oracle feed. To incentivize liquidity for OVL, a portion of protocol trading fees would be allocated to spot market liquidity providers through a community governed treasury. We also propose an incentivized insurance fund as a fail-safe to curb excessive expansion of the OVL currency supply.

## Motivation
<!--This is the problem statement. This is the *why* of the OIP. It should clearly explain *why* the current state of the protocol is inadequate.  It is critical that you explain *why* the change is needed, if the OIP proposes changing how something is calculated, you must address *why* the current calculation is innaccurate or wrong. This is not the place to describe how the OIP will address the issue!-->
This is the problem statement. This is the *why* of the OIP. It should clearly explain *why* the current state of the protocol is inadequate.  It is critical that you explain *why* the change is needed, if the OIP proposes changing how something is calculated, you must address *why* the current calculation is innaccurate or wrong. This is not the place to describe how the OIP will address the issue!

## Specification
<!--The specification should describe the syntax and semantics of any new feature, there are five sections
1. Overview
2. Rationale
3. Technical Specification
4. Test Cases
5. Configurable Values
-->

### Overview
<!--This is a high level overview of *how* the OIP will solve the problem. The overview should clearly describe how the new feature will be implemented.-->
This is a high level overview of *how* the OIP will solve the problem. The overview should clearly describe how the new feature will be implemented.

### Rationale
<!--This is where you explain the reasoning behind how you propose to solve the problem. Why did you propose to implement the change in this way, what were the considerations and trade-offs. The rationale fleshes out what motivated the design and why particular design decisions were made. It should describe alternate designs that were considered and related work. The rationale may also provide evidence of consensus within the community, and should discuss important objections or concerns raised during discussion.-->
This is where you explain the reasoning behind how you propose to solve the problem. Why did you propose to implement the change in this way, what were the considerations and trade-offs. The rationale fleshes out what motivated the design and why particular design decisions were made. It should describe alternate designs that were considered and related work. The rationale may also provide evidence of consensus within the community, and should discuss important objections or concerns raised during discussion.

### Technical Specification
<!--The technical specification should outline the public API of the changes proposed. That is, changes to any of the interfaces Overlay currently exposes or the creations of new ones.-->
The technical specification should outline the public API of the changes proposed. That is, changes to any of the interfaces Overlay currently exposes or the creations of new ones.

### Test Cases
<!--Test cases for an implementation are mandatory for OIPs but can be included with the implementation..-->
Test cases for an implementation are mandatory for OIPs but can be included with the implementation.

## Copyright
Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
