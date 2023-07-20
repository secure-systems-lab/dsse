# DSSE Envelope

May 10, 2024

Version 1.1.0

This document describes the recommended data structure for storing DSSE
signatures, which we call the "JSON Envelope". For the protocol/algorithm, see
[Protocol](protocol.md).

## Standard JSON envelope

See [envelope.proto](envelope.proto) for a formal schema. (Protobuf is used only
to define the schema. JSON is the only recommended encoding.)

The standard data structure for storing a signed message is a JSON message of
the following form, called the "JSON envelope":

```json
{
  "payload": "<Base64(SERIALIZED_BODY)>",
  "payloadType": "<PAYLOAD_TYPE>",
  "signatures": [{
    "keyid": "<KEYID>",
    "sig": "<Base64(SIGNATURE)>"
  }]
}
```

See [Protocol](protocol.md) for a definition of parameters and functions.

Base64() is [Base64 encoding](https://tools.ietf.org/html/rfc4648), transforming
a byte sequence to a unicode string. Either standard or URL-safe encoding is
allowed.

### Multiple signatures

An envelope MAY have more than one signature, which is equivalent to separate
envelopes with individual signatures.

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

### Signature Extensions [experimental]


NOTE: The design for signature extensions is currently experimental and may
change.

In addition to `keyid` and `sig`, a signature object may include an `extension`
field to store ecosystem specific information pertaining to the signature.
Extensions do not modify the signing workflow established in the
[DSSE protocol](protocol.md) except for actually encoding the extension
alongside the signature in the envelope. However, signers and verifiers may
exchange information about the extensions used out-of-band.

```json
{
  "payload": "<Base64(SERIALIZED_BODY)>",
  "payloadType": "<PAYLOAD_TYPE>",
  "signatures": [{
    "keyid": "<KEYID>",
    "sig": "<Base64(SIGNATURE)>",
    "extension": {
      "kind": "<EXTENSION_KIND>",
      "ext": {...}
    }
  }]
}
```

`extension.kind` is a string and the `EXTENSION_KIND` value must unambiguously
identify the ecosystem or kind of the extension. This in turn identifies the
fields in the opaque object `ext`. Some well-known extensions MAY be
[registered and listed](extensions.md) with their `ext` definition alongside the
DSSE specification.

Additionally, extensions MUST NOT contain any information such that the
signature verification fails in its presence and passes in its absence.
Essentially, if a required extension in some context is missing or if a consumer
does not recognize the extension, verification MUST fail closed.

Finally, the opaque `ext` MUST NOT contain a DSSE envelope to avoid recursive
verification of extensions and signatures. Similarly, the `ext` MUST NOT provide
the signature bytes itself, but MUST only contain information required to verify
the signature recorded in `sig` field.

### Parsing rules

*   The following fields are REQUIRED and MUST be set, even if empty: `payload`,
    `payloadType`, `signature`, `signature.sig`.
*   The following fields are OPTIONAL and MAY be unset: `signature.keyid`,
    `signature.extension`. An unset field MUST be treated the same as
    set-but-empty.
*   The schema for `signature.extension.ext` for some declared
    `signature.extension.kind` MUST be communicated separately by producers to
    consumers.
*   Producers, or future versions of the spec, MAY add additional fields.
    Consumers MUST ignore unrecognized fields. Similarly, consumers MUST ignore
    extensions of an unrecognized kind.

## Other data structures

The standard envelope is JSON message with an explicit `payloadType`.
Optionally, applications may encode the signed message in other methods without
invalidating the signature:

-   An encoding other than JSON, such as CBOR or protobuf.
-   Use a default `payloadType` if omitted and/or code `payloadType` as a
    shorter string or enum.

At this point we do not standardize any other encoding. If a need arises, we may
do so in the future.
