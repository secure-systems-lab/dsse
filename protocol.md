# signing-spec Protocol

March 03, 2021

Version 0.1.0

This document describes the protocol/algorithm for creating and verifying
signing-spec signatures, independent of how they are transmitted or stored. For
the recommended data structure, see [Envelope](envelope.md).

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

*   SERIALIZED_BODY: Byte sequence to be signed.

*   PAYLOAD_TYPE: Authenticated URI indicating how to interpret SERIALIZED_BODY.
    It encompasses the content type (JSON, Canonical-JSON, CBOR, etc.), the
    purpose, and the schema version of the payload. This obviates the need for
    the `_type` field within [in-toto]/[TUF] payloads. This URI does not need to
    be resolved to a remote resource, nor does such a resource need to be
    fetched. Examples: `https://in-toto.io/Link/v1.0`,
    `https://in-toto.io/Layout/v1.0`,
    `https://theupdateframework.com/Root/v1.0.5`.

*   KEYID: Optional, unauthenticated hint indicating what key and algorithm was
    used to sign the message. As with Sign(), details are agreed upon
    out-of-band by the signer and verifier. It **MUST NOT** be used for security
    decisions; it may only be used to narrow the selection of possible keys to
    try.

Functions:

*   PAE() is the
    [PASETO Pre-Authentication Encoding](https://github.com/paragonie/paseto/blob/master/docs/01-Protocol-Versions/Common.md#authentication-padding),
    where parameters `type` and `body` are byte sequences:

    ```none
    PAE(type, body) := le64(2) || le64(len(type)) || type || le64(len(body)) || body
    le64(n) := 64-bit little-endian encoding of `n`, where 0 <= n < 2^63
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

## Test Vectors

See [reference implementation](reference_implementation.ipynb). Here is an
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
02 00 00 00 00 00 00 00 1d 00 00 00 00 00 00 00
68 74 74 70 3a 2f 2f 65 78 61 6d 70 6c 65 2e 63
6f 6d 2f 48 65 6c 6c 6f 57 6f 72 6c 64 0b 00 00
00 00 00 00 00 68 65 6c 6c 6f 20 77 6f 72 6c 64
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
 "signatures": [{"sig": "y7BK8Mm8Mr4gxk4+G9X3BD1iBc/vVVuJuV4ubmsEK4m/8MhQOOS26ejx+weIjyAx8VjYoZRPpoXSNjHEzdE7nQ=="}]}
```

[Canonical JSON]: http://wiki.laptop.org/go/Canonical_JSON
[in-toto]: https://in-toto.io
[JWS]: https://tools.ietf.org/html/rfc7515
[PASETO]: https://github.com/paragonie/paseto/blob/master/docs/01-Protocol-Versions/Version2.md#sig
[TUF]: https://theupdateframework.io
