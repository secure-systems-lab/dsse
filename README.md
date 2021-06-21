# DSSE: Dead Simple Signing Envelope

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

*   Key management / PKI /
    [exclusive ownership](https://www.bolet.org/~pornin/2005-acns-pornin+stern.pdf)

## Why not...?

*   Why not raw signatures? Too fragile.
*   Why not [JWS](https://tools.ietf.org/html/rfc7515)? Too many insecure
    implementations and features.
*   Why not [PASETO](https://paseto.io)? JSON-specific, too opinionated.
*   Why not the legacy TUF/in-toto signature scheme? JSON-specific, relies on
    canonicalization.

See [Background](background.md) for further motivation.

## Who uses it?

<!-- Reminder: once in-toto and TUF switch to this new format, update the rest
of the docs that currently reference the old format as "current", "existing",
etc. -->

*   [in-toto](https://in-toto.io) (pending [ITE-5](https://github.com/in-toto/ITE/pull/13))
*   [TUF](https://theupdateframework.io) (pending)
