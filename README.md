# OIPs

Overlay Improvement Proposals (OIPs) describe standards for the Overlay platform, including core protocol specifications, client APIs, and contract standards.

## Contributing

 1. Review [OIP-0](OIPs/OIP-0.md).
 2. Fork the repository by clicking "Fork" in the top right.
 3. Add your OIP to your fork of the repository. There is a [template OIP here](OIP-X.md).
 4. Submit a Pull Request to Overlay's [OIPs repository](https://github.com/overlay-market/OIPs/).

Your first PR should be a first draft of the final OIP. It must meet the formatting criteria enforced by the build (largely, correct metadata in the header). An editor will manually review the first PR for a new OIP and assign it a number before merging it. Make sure you include a `discussions-to` header with the URL to a new thread on [gov.overlay.market](https://gov.overlay.market/) where people can discuss the OIP as a whole.

If your OIP requires images, the image files should be included in a subdirectory of the `assets` folder for that OIP as follow: `assets/OIP-X` (for OIP **X**). When linking to an image in the OIP, use relative links such as `../assets/OIP-X/image.png`.

When you believe your OIP is mature and ready to progress past the WIP phase, you should ask to have your issue added to the next governance call where it can be discussed for inclusion in a future platform upgrade. If the community agrees to include it, the OIP editors will update the state of your OIP to 'Approved'.

## OIP Statuses

* **WIP** - a OIP that is still being developed.
* **Proposed** - a OIP that is ready to be reviewed in a governance call.
* **Approved** - a OIP that has been accepted for implementation by the Overlay community.
* **Implemented** - a OIP that has been released to mainnet.
* **Rejected** - a OIP that has been rejected.
* **Withdrawn** - a OIP that has been withdrawn by the author(s).
* **Deferred** - a OIP that is pending another OIP/some other change that should be bundled with it together.
* **Moribund** - a OIP that was implemented but is now obsolete and requires no explicit replacement.

## Validation

OIPs must pass some validation tests.  The OIP repository ensures this by running tests using [html-proofer](https://rubygems.org/gems/html-proofer) and [OIP_validator](https://rubygems.org/gems/OIP_validator).

It is possible to run the OIP validator locally:
```
gem install OIP_validator
OIP_validator <INPUT_FILES>
```

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
