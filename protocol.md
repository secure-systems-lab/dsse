# DSSE Protocol

March 03, 2021

Version 1.0.0

This document describes the protocol/algorithm for creating and verifying DSSE
signatures, independent of how they are transmitted or stored. For the
recommended data structure, see [Envelope](envelope.md).

## Signature Definition

A signature is defined as:

```none
SIGNATURE = Sign(PAE(UTF8(PAYLOAD_TYPE), SERIALIZED_BODY))
```

Parameters:

Name            | Type   | Required | Authenticated
--------------- | ------ | -------- | -------------
SERIALIZED_BODY | bytes  | Yes      | Yes
PAYLOAD_TYPE    | string | Yes      | Yes
KEYID           | string | No       | No

*   SERIALIZED_BODY: Arbitrary byte sequence to be signed.

*   PAYLOAD_TYPE: Opaque, case-sensitive string that uniquely and unambiguously
    identifies how to interpret `payload`. This includes both the encoding
    (JSON, CBOR, etc.) as well as the meaning/schema. To prevent collisions, the
    value SHOULD be either:

    *   [Media Type](https://www.iana.org/assignments/media-types/), a.k.a. MIME
        type or Content Type
        *   Example: `application/vnd.in-toto+json`.
        *   IMPORTANT: This SHOULD be an application-specific type describing
            both encoding and schema, NOT a generic type like
            `application/json`. The problem with generic types is that two
            different applications could use the same encoding (e.g. JSON) but
            interpret the payload differently.
        *   SHOULD be lowercase.
    *   [URI](https://tools.ietf.org/html/rfc3986)
        *   Example: `https://example.com/MyMessage/v1-json`.
        *   SHOULD resolve to a human-readable description but MAY be
            unresolvable.
        *   SHOULD be case-normalized (section 6.2.2.1)

*   KEYID: Optional, unauthenticated hint indicating what key and algorithm was
    used to sign the message. As with Sign(), details are agreed upon
    out-of-band by the signer and verifier. It **MUST NOT** be used for security
    decisions; it may only be used to narrow the selection of possible keys to
    try.

Functions:

*   PAE() is the "Pre-Authentication Encoding", where parameters `type` and
    `body` are byte sequences:

    ```none
    PAE(type, body) = "DSSEv1" + SP + LEN(type) + SP + type + SP + LEN(body) + SP + body
    +               = concatenation
    SP              = ASCII space [0x20]
    "DSSEv1"        = ASCII [0x44, 0x53, 0x53, 0x45, 0x76, 0x31]
    LEN(s)          = ASCII decimal encoding of the byte length of s, with no leading zeros
    ```

*   Sign() is an arbitrary digital signature format. Details are agreed upon
    out-of-band by the signer and verifier. This specification places no
    restriction on the signature algorithm or format.

*   UTF8() is [UTF-8 encoding](https://tools.ietf.org/html/rfc3629),
    transforming a unicode string to a byte sequence.

## Protocol

Out of band:

-   Agree on a PAYLOAD_TYPE and cryptographic details, optionally including
    KEYID.

To sign:

-   Serialize the message according to PAYLOAD_TYPE. Call the result
    SERIALIZED_BODY.
-   Sign PAE(UTF8(PAYLOAD_TYPE), SERIALIZED_BODY). Call the result SIGNATURE.
-   Optionally, compute a KEYID.
-   Encode and transmit SERIALIZED_BODY, PAYLOAD_TYPE, SIGNATURE, and KEYID,
    preferably using the recommended [JSON envelope](envelope.md).

To verify:

-   Receive and decode SERIALIZED_BODY, PAYLOAD_TYPE, SIGNATURE, and KEYID, such
    as from the recommended [JSON envelope](envelope.md). Reject if decoding
    fails.
-   Optionally, filter acceptable public keys by KEYID.
-   Verify SIGNATURE against PAE(UTF8(PAYLOAD_TYPE), SERIALIZED_BODY). Reject if
    the verification fails.
-   Reject if PAYLOAD_TYPE is not a supported type.
-   Parse SERIALIZED_BODY according to PAYLOAD_TYPE. Reject if the parsing
    fails.

Either standard or URL-safe base64 encodings are allowed. Signers may use
either, and verifiers **MUST** accept either.

## Multi-signature Verification

Multi-signature enhances the security by allowing multiple signers to sign the
same payload. The resulting signatures are encoded and transmitted, preferably
using the recommended [JSON envelope](envelope.md).

A `(t, n)`-ENVELOPE is valid if the enclosed signatures pass the verification
against at least `t` of `n` unique trusted public keys where `t` is
application-specific.

To verify a `(t, n)`-ENVELOPE:

-   Receive and decode SERIALIZED_BODY, PAYLOAD_TYPE, SIGNATURES from ENVELOPE.
    Reject if decoding fails.
-   For each (SIGNATURE, KEYID) in SIGNATURES,
    -   Optionally, filter acceptable public keys by KEYID.
    -   Verify SIGNATURE against PAE(UTF8(PAYLOAD_TYPE), SERIALIZED_BODY). Skip
        over if the verification fails.
    -   Add the accepted public key to the set ACCEPTED_KEYS.
    -   Break if the number of unique keys in ACCEPTED_KEYS is greater or equal
        to `t`.
-   Reject if the unique keys in ACCEPTED_KEYS is less than `t`.
-   Reject if PAYLOAD_TYPE is not a supported type.
-   Parse SERIALIZED_BODY according to PAYLOAD_TYPE. Reject if the parsing
    fails.

## Test Vectors

See [reference implementation](implementation/signing_spec.py). Here is an
example.

SERIALIZED_BODY:

```none
hello world
```

PAYLOAD_TYPE:

```none
http://example.com/HelloWorld
```

PAE:

```none
DSSEv1 29 http://example.com/HelloWorld 11 hello world
```

Cryptographic keys:

```none
Algorithm: ECDSA over NIST P-256 and SHA-256, with deterministic-rfc6979
Signature: raw concatenation of r and s (Cryptodome binary encoding)
X: 46950820868899156662930047687818585632848591499744589407958293238635476079160
Y: 5640078356564379163099075877009565129882514886557779369047442380624545832820
d: 97358161215184420915383655311931858321456579547487070936769975997791359926199
```

Result (using the recommended [JSON envelope](envelope.md)):

```json
{"payload": "aGVsbG8gd29ybGQ=",
 "payloadType": "http://example.com/HelloWorld",
 "signatures": [{"sig": "A3JqsQGtVsJ2O2xqrI5IcnXip5GToJ3F+FnZ+O88SjtR6rDAajabZKciJTfUiHqJPcIAriEGAHTVeCUjW2JIZA=="}]}
```

[Canonical JSON]: http://wiki.laptop.org/go/Canonical_JSON
[in-toto]: https://in-toto.io
[JWS]: https://tools.ietf.org/html/rfc7515
[PASETO]: https://github.com/paragonie/paseto/blob/master/docs/01-Protocol-Versions/Version2.md#sig
[TUF]: https://theupdateframework.io
