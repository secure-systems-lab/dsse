# $signing_spec

A signature scheme for software supply chain metadata that avoids
canonicalization

November 25, 2020

Version 0.1.0

## Abstract

This document proposes a new signature scheme for use by, among others, the
in-toto and TUF projects. This signature scheme (a) avoids relying on
canonicalization for security and (b) reduces the possibility of
misinterpretation of the payload. The serialized payload is encoded as a string
and verified by the recipient _before_ deserializing. A backwards compatible
variant is available.

## Overview

$signing_spec does not rely on Canonical JSON, nor any other canonicalization
scheme. Instead, the producer records the signed bytes exactly as signed and the
consumer verifies those exact bytes before parsing. In addition, the signature
now includes an authenticated `payloadType` field indicating how to interpret
the payload.

## Specification

The signature format is a JSON message of the following form:

```json
{
  "payload": "<Base64(SERIALIZED_BODY)>",
  "payloadType": "<PAYLOAD_TYPE>",
  "signatures": [{
    "keyid": "<KEYID>",
    "sig": "<Base64(Sign(PAE(UTF8(PAYLOAD_TYPE), SERIALIZED_BODY)))>"
  }]
}
```

Empty fields may be omitted. [Multiple signatures](#multiple-signatures) are
allowed. Note that an optional `signature.sigType` field may be present but
empty for compatibility with [backwards compatible signature] mode.

Parameters:

*   SERIALIZED_BODY is the byte sequence to be signed.

*   PAYLOAD_TYPE is an authenticated(*) URI indicating how to interpret
    SERIALIZED_BODY. It encompasses the content type (JSON, Canonical-JSON,
    CBOR, etc.), the purpose, and the schema version of the payload. This
    obviates the need for the `_type` field within in-toto/TUF payloads. This
    URI does not need to be resolved to a remote resource, nor does such a
    resource need to be fetched. Examples:

    -   https://in-toto.io/Link/v0.9
    -   https://in-toto.io/Layout/v0.9
    -   https://theupdateframework.com/Root/v1.0.5
    -   etc...

    (*) Exception: PAYLOAD_TYPE is unauthenticated if `signature.sigType ==
    "raw-json-no-payload-type"`.

*   KEYID is an optional, unauthenticated hint indicating what key and algorithm
    was used to sign the message. As with Sign(), details are agreed upon
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

*   Base64() is [Base64 encoding](https://tools.ietf.org/html/rfc4648),
    transforming a byte sequence to a unicode string. Either standard or
    URL-safe encoding is allowed.

### Steps

Out of band:

-   Agree on a PAYLOAD_TYPE and cryptographic details.
-   Decide if [backwards compatible signature] mode should be allowed.

To sign:

-   Serialize the message according to PAYLOAD_TYPE. Call the result
    SERIALIZED_BODY.
-   Sign PAE(UTF8(PAYLOAD_TYPE), SERIALIZED_BODY), base64-encode the result, and
    store it in `sig`.
-   Optionally, compute a KEYID and store it in `keyid`.
-   Base64-encode SERIALIZED_BODY and store it in `payload`.
-   Store PAYLOAD_TYPE in `payloadType`.

To verify:

-   If `sigType == "raw-json-no-payload-type"`, use
    [backwards compatible signature] instead. Reject if `sigType` is any other
    non-empty value.
-   Base64-decode `payload`; call this SERIALIZED_BODY. Reject if the decoding
    fails.
-   Base64-decode `sig` and verify PAE(UTF8(PAYLOAD_TYPE), SERIALIZED_BODY).
    Reject if either the decoding or the signature verification fails.
-   Reject if PAYLOAD_TYPE is not a supported type.
-   Parse SERIALIZED_BODY according to PAYLOAD_TYPE. Reject if the parsing
    fails.

Either standard or URL-safe base64 encodings are allowed. Signers may use
either, and verifiers **MUST** accept either.

### Backwards compatible signatures

To convert existing signatures from the current format to the new format,
`"backwards-compatible-json"` is added to the payload type URI to indicate that
the signature is over the raw payload. This allows the signatures to remain
valid while avoiding the verifier from having to use [Canonical JSON].

```json
{
  "payload": "<Base64(SERIALIZED_BODY)>",
  "signatures" : [{
    "keyid": "<KEYID>",
    "sigType": "raw-json-no-payload-type",
    "sig" : "<Base64(Sign(SERIALIZED_BODY))>"
  }]
}
```

Support for this backwards compatibility mode is optional and should be disabled
by default.

To sign:

-   The message **MUST** be an object type (`{...}`).
-   Serialize the message as [Canonical JSON]; call this SERIALIZED_BODY.
-   Sign SERIALIZED_BODY, base64-encode the result, and store it in `sig`.
-   Store `"raw-json-no-payload-type"` in `sigType`.
-   Optionally, compute a KEYID and store it in `keyid`.
-   Base64-encode SERIALIZED_BODY and store it in `payload`.

To verify:

-   If `sigType != "raw-json-no-payload-type"`, use the
    [normal verification process](#steps) instead of this one.
-   Base64-decode `payload`; call this SERIALIZED_BODY. Reject if the decoding
    fails.
-   Base64-decode `sig` and verify SERIALIZED_BODY. Reject if either the
    decoding or the signature verification fails.
-   Parse SERIALIZED_BODY as a JSON object. Reject if the parsing fails or if
    the result is not a JSON object. In particular, the first byte of
    SERIALIZED_BODY **MUST** be `{`. Verifiers **MUST NOT** require SERIALIZED_BODY
    to be Canonical JSON.
-   Discard `payloadType` if present.

Backwards compatible signatures are not recommended because they lack the
authenticated payloadType indicator.

This scheme is safe from rollback attacks because the first byte of
SERIALIZED_BODY is 0x7b (`{`) in backwards compatibility mode and 0x02 in
regular mode.

### Multiple signatures

A file may have more than one signature, which is equivalent to separate files
with individual signatures.

```json
{
  "payload": "<Base64(SERIALIZED_BODY)>",
  "payloadType": "<PAYLOAD_TYPE>",
  "signatures": [{
      "keyid": "<KEYID_1>",
      "sig": "<SIG_1>"
    }, {
      "keyid": "<KEYID_2>",
      "sig": "<SIG_2>"
  }]
}
```

### Optional changes to wrapper

The standard wrapper is JSON with an explicit `payloadType`. Optionally,
applications may encode the wrapper in other methods without invalidating the
signature:

-   An encoding other than JSON, such as CBOR or Protobuf.
-   Use a default `payloadType` if omitted and/or code `payloadType` as a
    shorter string or enum.

At this point we do not standardize any other encoding. If a need arises, we may
do so in the future.

### Differentiating between old and new formats

Verifiers can differentiate between the old and new wrapper format by detecting
the presence of the `payload` field vs `signed` field.

## Motivation

There are two concerns with the current in-toto/TUF signature wrapper.

First, the signature scheme depends on [Canonical JSON], which has one practical
problem and two theoretical ones:

1.  Practical problem: It requires the payload to be JSON or convertible to
    JSON. While this happens to be true of in-toto and TUF today, a generic
    signature layer should be able to handle arbitrary payloads.
1.  Theoretical problem 1: Two semantically different payloads could have the
    same canonical encoding. Although there are currently no known attacks on
    Canonical JSON, there have been attacks in the past on other
    canonicalization schemes
    ([example](https://latacora.micro.blog/2019/07/24/how-not-to.html#canonicalization)).
    It is safer to avoid canonicalization altogether.
1.  Theoretical problem 2: It requires the verifier to parse the payload before
    verifying, which is both error-prone—too easy to forget to verify—and an
    unnecessarily increased attack surface.

The preferred solution is to transmit the encoded byte stream exactly as it was
signed, which the verifier verifies before parsing. This is what is done in
[JWS] and [PASETO], for example.

Second, the scheme does not include an authenticated "context" indicator to
ensure that the signer and verifier interpret the payload in the same exact way.
For example, if in-toto were extended to support CBOR and Protobuf encoding, the
signer could get a CI/CD system to produce a CBOR message saying X and then a
verifier to interpret it as a protobuf message saying Y. While we don't know of
an exploitable attack on in-toto or TUF today, potential changes could introduce
such a vulnerability. The signature scheme should be resilient against these
classes of attacks. See [example attack](hypothetical_signature_attack.ipynb)
for more details.

## Reasoning

Our goal was to create a signature wrapper that is as simple and foolproof as
possible. Alternatives such as [JWS] are extremely complex and error-prone,
while others such as [PASETO] are overly specific. (Both are also
JSON-specific.) We believe our proposal strikes the right balance of simplicity,
usefulness, and security.

Rationales for specific decisions:

-   Why use base64 for payload and sig?

    -   Because JSON strings do not allow binary data, so we need to either
        encode the data or escape it. Base64 is a standard, reasonably
        space-efficient way of doing so. Protocols that have a first-class
        concept of "bytes", such as protobuf or CBOR, do not need to use base64.

-   Why sign raw bytes rather than base64 encoded bytes (as per JWS)?

    -   Because it's simpler. Base64 is only needed for putting binary data in a
        text field, such as JSON. In other formats, such as protobuf or CBOR,
        base64 isn't needed at all.

-   Why does payloadType need to be signed?

    -   See [Motivation](#motivation).

-   Why use PAE?

    -   Because we need an unambiguous way of serializing two fields,
        payloadType and payload. PAE is already documented and good enough. No
        need to reinvent the wheel.

-   Why use a URI for payloadType rather than
    [Media Type](https://www.iana.org/assignments/media-types/media-types.xhtml)
    (a.k.a. MIME type)?

    -   Because Media Type only indicates how to parse but does not indicate
        purpose, schema, or versioning. If it were just "application/json", for
        example, then every application would need to impose some "type" field
        within the payload, lest we have similar vulnerabilities as if
        payloadType were not signed.
    -   Also, URIs don't need to be registered while Media Types do.

-   Why use payloadType "backwards-compatible-json" instead of assuming
    backwards compatible mode if payloadType is absent?

    -   We wanted to leave open the possibility of having an
        application-specific "default" value if payloadType is unspecified,
        rather than forcing the default to be backwards compatibility mode.
    -   Note that specific applications can still choose backwards compatibility
        to be the default.

-   Why not stay backwards compatible by requiring the payload to always be JSON
    with a "_type" field? Then if you want a non-JSON payload, you could simply
    have a field that contains the real payload, e.g. `{"_type":"my-thing",
    "value":"base64…"}`.

    1.  It encourages users to add a "_type" field to their payload, which in
        turn:
        -   (a) Ties the payload type to the authentication type. Ideally the
            two would be independent.
        -   (b) May conflict with other uses of that same field.
        -   (c) May require the user to specify type multiple times with
            different field names, e.g. with "@context" for
            [JSON-LD](https://json-ld.org/).
    2.  It would incur double base64 encoding overhead for non-JSON payloads.
    3.  It is more complex than PAE.

## Backwards compatibility with existing TUF and in-toto signatures

### Current format

The
[old signature format](https://github.com/in-toto/docs/blob/master/in-toto-spec.md#42-file-formats-general-principles)
used by TUF and in-toto has a BODY that is a regular JSON object and a signature
over the [Canonical JSON] serialization of BODY.

```json
{
  "signed": <BODY>,
  "signatures": [{
    "keyid": "<KEYID>",
    "sig": "<Hex(Sign(CanonicalJson(BODY)))>"
  }]
}
```

To verify, the consumer parses the whole JSON file, re-serializes BODY using
Canonical JSON, then verifies the signature.

### Detect if a document is using old format

To detect whether a signature is in the old or new format:

-   If it contains a `payload` field, assume it is in the new format.
-   If it contains a `signed` field, assume it is in the old format.

To convert an existing signature to the new format:

-   `new.payload = base64encode(CanonicalJson(orig.signed))`
-   `new.signatures[*].sigType = "raw-json-no-payload-type"`
-   `new.signatures[*].sig = base64encode(hexdecode(orig.signatures[*].sig))`
-   `new.signatures[*].keyid = orig.signatures[*].keyid`

To convert a [backwards compatible signature] to the old format:

-   `old.signed = jsonparse(base64decode(new.payload))`
-   `old.signatures[*].sig = hexencode(base64decode(new.signatures[*].sig))`
-   `old.signatures[*].keyid = new.signatures[*].keyid`

## Testing

TODO: Update reference implementation with this new design.

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

Signed wrapper:

```json
{"payload": "aGVsbG8gd29ybGQ=",
 "payloadType": "http://example.com/HelloWorld",
 "signatures": [{"sig": "y7BK8Mm8Mr4gxk4+G9X3BD1iBc/vVVuJuV4ubmsEK4m/8MhQOOS26ejx+weIjyAx8VjYoZRPpoXSNjHEzdE7nQ=="}]}
```

## References

-   [Canonical JSON]
-   [JWS]
-   [PASETO]

[backwards compatible signature]: #backwards-compatible-signatures
[Canonical JSON]: http://wiki.laptop.org/go/Canonical_JSON
[JWS]: https://tools.ietf.org/html/rfc7515
[PASETO]: https://github.com/paragonie/paseto/blob/master/docs/01-Protocol-Versions/Version2.md#sig
