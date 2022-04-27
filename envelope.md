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
    "sig": "<Base64(SIGNATURE)>",
    "cert": "<PEM(CERTIFICATE_CHAIN)>"
  }]
}
```

See [Protocol](protocol.md) for a definition of parameters and functions.

Base64() is [Base64 encoding](https://tools.ietf.org/html/rfc4648), transforming
a byte sequence to a unicode string. Either standard or URL-safe encoding is
allowed.

PEM() is a [PEM encoding](), transforming a DER (binary) encoded X.509 certificate to a base64 encoding with a one-line header and footer.

### Multiple signatures

An envelope MAY have more than one signature, which is equivalent to separate
envelopes with individual signatures.

```json
{
  "payload": "<Base64(SERIALIZED_BODY)>",
  "payloadType": "<PAYLOAD_TYPE>",
  "signatures": [{
      "keyid": "<KEYID_1>",
      "sig": "<SIG_1>",
      "cert": "<CERT_1>"
    }, {
      "keyid": "<KEYID_2>",
      "sig": "<SIG_2>",
      "cert": "<CERT_2>"
  }]
}
```

### Parsing rules

*   The following fields are REQUIRED and MUST be set, even if empty: `payload`,
    `payloadType`, `signature`, `signature.sig`.
*   The following fields are OPTIONAL and MAY be unset: `signature.keyid`, `signature.cert`
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
