# Background

## What is the intended use case?

This can be used anywhere digital signatures are needed.

The initial application is for signing software supply chain metadata in [TUF]
and [in-toto].

## Why do we need this?

There is no other simple, foolproof signature scheme that we are aware of.

*   Raw signatures are too fragile. Every public key must be used for exactly
    one purpose over exactly one message type, lest the system be vulnerable to
    [confusion attacks](#motivation). In many cases, this results in a difficult
    key management problem.

*   [TUF] and [in-toto] currently use a scheme that avoids these problems but is
    JSON-specific and relies on [canonicalization](motivation.md), which is an
    unnecessarily large attack surface.

*   [JWS], though popular, has a history of
    [vulnerable implementations](https://auth0.com/blog/critical-vulnerabilities-in-json-web-token-libraries/)
    due to the complexity and lack of specificity in the RFC, such as not
    verifying that `alg` matches the public key type or not verifying the root
    CA for `x5c`. It also requires a JSON library even if the payload is not
    JSON, though this is a minor issue.

*   [PASETO] is JSON-specific and too opinionated. For example, it mandates
    ed25519 signatures, which may not be useful in all cases.

The intent of this project is to define a minimal signature scheme that avoids
these issues.

## Design requirements

The [protocol](protocol.md):

*   MUST reduce the possibility of a client misinterpreting the payload (e.g.
    interpreting a JSON message as protobuf)
*   MUST support arbitrary payload types (e.g. not just JSON)
*   MUST support arbitrary crypto primitives, libraries, and key management
    systems (e.g. Tink vs openssl, Google KMS vs Amazon KMS)
*   SHOULD avoid depending on canonicalization for security
*   SHOULD NOT require unnecessary encoding (e.g. base64)
*   SHOULD NOT require the verifier to parse the payload before verifying

The [data structure](envelope.md):

*   MUST include both message and signature(s)
    *   NOTE: Detached signatures are supported by having the included message
        contain a cryptographic hash of the external data.
*   MUST support multiple signatures in one structure / file
*   SHOULD discourage users from reading the payload without verifying the
    signatures
*   SHOULD be easy to parse using common libraries (e.g. JSON)
*   SHOULD support a hint indicating what signing key was used

## Motivation

There are two concerns with the current [in-toto]/[TUF] signature envelope.

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
For example, if in-toto were extended to support CBOR and protobuf encoding, the
signer could get a CI/CD system to produce a CBOR message saying X and then a
verifier to interpret it as a protobuf message saying Y. While we don't know of
an exploitable attack on in-toto or TUF today, potential changes could introduce
such a vulnerability. The signature scheme should be resilient against these
classes of attacks. See [example attack](hypothetical_signature_attack.ipynb)
for more details.

## Reasoning

Our goal was to create a signature envelope that is as simple and foolproof as
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

## Backwards Compatibility

Backwards compatibility with the old [in-toto]/[TUF] format will be handled by
the application and explained in the corresponding application-specific change
proposal, namely [ITE-5](https://github.com/in-toto/ITE/pull/13) for in-toto and
via the principles laid out in
[TAP-14](https://github.com/theupdateframework/taps/blob/master/tap14.md) for
TUF.

Verifiers can differentiate between the
[old](https://github.com/in-toto/docs/blob/master/in-toto-spec.md#42-file-formats-general-principles)
and new envelope format by detecting the presence of the `payload` field (new
format) vs `signed` field (old format).

[Canonical JSON]: http://wiki.laptop.org/go/Canonical_JSON
[in-toto]: https://in-toto.io
[JWS]: https://tools.ietf.org/html/rfc7515
[PASETO]: https://github.com/paragonie/paseto/blob/master/docs/01-Protocol-Versions/Version2.md#sig
[TUF]: https://theupdateframework.io
