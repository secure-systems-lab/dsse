# DSSE Extensions

May 10, 2024

Version 1.1.0

This document lists the well known DSSE
[signature extensions](/envelope.md#signature-extensions). To add a signature
extension, propose a change with a unique media type for the signing ecosystem
and include a link to the format of the `ext` field.

| Name (with link) | Kind | Notes |
|------------------|------|-------|
| [Sigstore] | `application/vnd.dev.sigstore.verificationmaterial;version=<VERSION>` | The X.509 certificate chain must not include the root or trusted intermediate certificates |


[Sigstore]: https://github.com/sigstore/protobuf-specs/blob/main/protos/sigstore_bundle.proto
