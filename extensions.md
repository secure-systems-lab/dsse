# DSSE Extensions

August 21, 2023

Version 1.1.0-draft

This document lists the well known DSSE
[signature extensions](/envelope.md#signature-extensions).

| Name (with link) | Kind | Notes |
|------------------|------|-------|
| [Sigstore] | `application/vnd.dev.sigstore.verificationmaterial;version=<VERSION>` | The X.509 certificate chain must not include the root or trusted intermediate certificates |


[Sigstore]: https://github.com/sigstore/protobuf-specs/blob/main/protos/sigstore_bundle.proto
