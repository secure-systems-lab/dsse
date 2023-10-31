# DSSE Envelope

March 03, 2021

Version 1.1.0

This document describes the recommended data structure for storing DSSE
signatures, which we call the "JSON Envelope". For the protocol/algorithm, see
[Protocol](protocol.md).

## Standard JSON envelope

See [envelope.proto](envelope.proto) for a formal schema. (Protobuf is used only
to define the schema. JSON is the only recommended encoding.)

The standard data structure for storing a signed message is a JSON message of
the following form, called the "JSON envelope":

```jsonc
{
  // Exactly one of the following must be set:
  "payload": "<Base64Encode(SERIALIZED_BODY)>",
  "payloadUtf8": "<Utf8Decode(SERIALIZED_BODY)>",
  // End oneof
  "payloadType": "<PAYLOAD_TYPE>",
  "signatures": [{
    "keyid": "<KEYID>",
    "sig": "<Base64(SIGNATURE)>"
  }]
}
```

See [Protocol](protocol.md) for a definition of parameters and functions.

Exactly one of `payload` or `payloadUtf8` MUST be set:

-   `payload` supports arbitrary SERIALIZED_BODY. 
    [Base64Encode()](https://tools.ietf.org/html/rfc4648) transforms a byte
    sequence to a Unicode string. Base64 has a fixed 33% space overhead but
    supports payloads that are not necessarily valid UTF-8. Either standard or
    URL-safe encoding is allowed.

-   `payloadUtf8` only supports valid
    [UTF-8](https://tools.ietf.org/html/rfc3629) SERIALIZED_BODY. `Utf8Decode()`
    converts that UTF-8 byte sequence to a Unicode string. Regular JSON string
    escaping applies, but this is usually more compact and amenable to
    compression than Base64.

Note: The choice of `payload` vs `payloadUtf8` does not impact the
[the signing or the signatures](protocol.md#signature-definition).

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

*   The following fields are REQUIRED and MUST be set, even if empty:
    exactly one of {`payload` or `payloadUtf8`}, `payloadType`, `signature`, `signature.sig`.
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

## Change history
* 1.1.0:
    * Added support for UTF-8 encoded payload and `payloadUtf8` field.

* 1.0.0: Initial version.

