# signing-spec

Simple, foolproof standard for signing arbitrary data.

## Features

*   Supports arbitrary message encodings, not just JSON.
*   Authenticates the message *and* the type to avoid confusion attacks.
*   Avoids canonicalization to reduce attack surface.
*   Allows any desired crypto primitives or libraries.

See [Background](background.md) for more information, including design
considerations and rationale.

## What is it?

Specifications for:

*   [Protocol](protocol.md) (*required*)
*   [Data structure](envelope.md), a.k.a. "Envelope" (*recommended*)
*   (pending #9) Suggested crypto primitives

Out of scope (for now at least):

*   Key management / PKI

## Why not...?

*   Why not raw signatures? Too fragile.
*   Why not [JOSE/JWS/JWT](https://jwt.io)? JSON-specific, too complicated, too
    easy to mess up.
*   Why not [PASETO](https://paseto.io)? JSON-specific, too opinionated.

See [Background](background.md) for further motivation.

## Who uses it?

*   [in-toto](https://in-toto.io) (pending [ITE-5](https://github.com/in-toto/ITE/pull/13))
*   [TUF](https://theupdateframework.io) (pending)
