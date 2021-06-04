# DSSE Envelope

March 03, 2021

Version 1.0.0

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

Empty fields may be omitted. [Multiple signatures](#multiple-signatures) are
allowed.

Base64() is [Base64 encoding](https://tools.ietf.org/html/rfc4648), transforming
a byte sequence to a unicode string. Either standard or URL-safe encoding is
allowed.

### Multiple signatures

An envelope may have more than one signature, which is equivalent to separate
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

## Other data structures

The standard envelope is JSON message with an explicit `payloadType`.
Optionally, applications may encode the signed message in other methods without
invalidating the signature:

-   An encoding other than JSON, such as CBOR or protobuf.
-   Use a default `payloadType` if omitted and/or code `payloadType` as a
    shorter string or enum.

At this point we do not standardize any other encoding. If a need arises, we may
do so in the future.
