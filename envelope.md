# DSSE Envelope

May 10, 2024

Version 1.0.2

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

### Parsing rules

*   The following fields are REQUIRED and MUST be set, even if empty: `payload`,
    `payloadType`, `signature`, `signature.sig`.
*   The following fields are OPTIONAL and MAY be unset: `signature.keyid`.
    An unset field MUST be treated the same as set-but-empty.
*   Producers, or future versions of the spec, MAY add additional fields.
    Consumers MUST ignore unrecognized fields.

## Other data structures

The standard envelope is JSON message with an explicit `payloadType`.
Optionally, applications may encode the signed message in other methods without
invalidating the signature:

-   An encoding other than JSON, such as CBOR or protobuf.
-   Use a default `payloadType` if omitted and/or code `payloadType` as a
    shorter string or enum.

At this point we do not standardize any other encoding. If a need arises, we may
do so in the future.

## Security considerations

The following advisories are relevant to all envelope formats, not just the
standard JSON envelope.

**Important:** Implementations MUST ensure that the same payload bytes that are
verified are the ones sent to the application layer. In particular,
implementations MUST NOT re-parse the envelope after verification to pull out
the payload. Failure to adhere to this requirement can lead to security
vulnerabilities.
