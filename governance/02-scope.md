# Scope

Under the Community Specification License 1.0, this document defines the scope
of the specification the DSSE Working Group develops. The licensing
commitments made by each contributor, including the patent commitment, apply
to the specification as bounded by this scope.

## 1. In Scope

The Working Group develops and maintains:

*   **The signing and verification protocol** ([protocol.md](../protocol.md)):
    the definition of a signature as
    `Sign(PAE(UTF8(PAYLOAD_TYPE), SERIALIZED_BODY))`, the Pre-Authentication
    Encoding (PAE) that binds the payload bytes to the payload type before
    signing, and the procedures for signing, verification, and `(t, n)`
    multi-signature verification of a single payload.

*   **The envelope data structure** ([envelope.md](../envelope.md) and
    [envelope.proto](../envelope.proto)): the JSON envelope carrying `payload`,
    `payloadType`, and `signatures`, together with its parsing rules for
    required, optional, and unrecognized fields.

*   **The signature object**: each entry in `signatures`, consisting of a
    required signature value (`sig`) and an optional `keyid` — an
    unauthenticated hint identifying which public key was used, usable only to
    narrow the selection of keys to try.

*   **Payload type identification**: conventions for the `payloadType` string
    (Media Type or URI) that identifies both the encoding and the schema of
    the payload.

*   **Extensibility rules**: the requirement that consumers ignore
    unrecognized envelope fields, allowing producers and future versions of
    the specification to add fields without breaking verification.

*   **Envelope encodings**: JSON is the only recommended encoding. The Working
    Group may standardize additional encodings (such as CBOR or protobuf) in a
    future version; until it does, other encodings are permitted by
    applications but not specified here.

*   **Test vectors** accompanying the protocol.

## 2. Out of Scope

The Working Group does not develop, and this specification does not define:

*   **Cryptographic algorithms or signature formats.** `Sign()` is an
    arbitrary digital signature format whose details are agreed upon
    out-of-band by the signer and verifier. The specification places no
    restriction on the algorithm or format, carries no self-describing
    algorithm header, and defines no negotiation mechanism.

*   **Key management, trust establishment, and identity binding.** Key
    distribution, PKI, certificate validation, and trust roots are left to
    external systems. The `keyid` is not a key-management mechanism: it MUST
    NOT be used for security decisions.

*   **Payload canonicalization.** The payload is an arbitrary byte sequence
    (`SERIALIZED_BODY`) transmitted exactly as signed; the verifier verifies
    it before parsing. No normalization or canonicalization scheme is defined.

*   **Payload semantics.** The specification makes no assertions about the
    internal validity, schema, or meaning of the payload. It guarantees only
    that a specific sequence of bytes was signed under a declared payload
    type.

*   **Encryption and confidentiality.** The specification provides
    authentication and integrity only.

*   **Verification policy.** Which keys are trusted, which payload types are
    supported, and the threshold `t` in `(t, n)` verification are
    application-specific decisions made outside this specification.

Any changes of Scope are not retroactive.
