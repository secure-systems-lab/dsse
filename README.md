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

*   [in-toto](https://in-toto.io) (as described in [ITE-5](https://github.com/in-toto/ITE/blob/master/ITE/5/README.adoc), [go](https://github.com/in-toto/go-witness/tree/main/dsse), [python](https://github.com/in-toto/in-toto/blob/d8fa07f5c3c3e052319b1a9b0c06408cdf5b5185/in_toto/common_args.py#L170))
*   [TUF](https://theupdateframework.io) (pending implementation of [TAP-17](https://github.com/theupdateframework/taps/pull/138))
*   [gittuf](https://gittuf.dev) (implemented with extensions in [go](https://github.com/gittuf/gittuf/tree/main/internal/third_party/go-securesystemslib/dsse))
*   [Sigstore](https://sigstore.dev) supports DSSE as an [entry type](https://github.com/sigstore/rekor/tree/main/pkg/types/dsse)
*   [Chainguard Images](https://www.chainguard.dev/unchained/reproducing-chainguards-reproducible-image-builds) use sigstore and in-toto (see above), and support DSSE
*   [GUAC](https://guac.sh/) GUAC [supports DSSE entries](https://github.com/guacsec/guac/blob/main/pkg/ingestor/parser/dsse/parser_dsse.go) as a data type

## How can we use it?

* There is a Python implementation in [this repository](implementation/).
* There's a DSSE library for Go in [go-securesystemslib](https://github.com/secure-systems-lab/go-securesystemslib/tree/main/dsse).
* SigStore includes a [Go implementation](https://github.com/sigstore/sigstore/tree/main/pkg/signature/dsse)
  that supports hardware tokens, cloud KMS systems, and more.

## Versioning

The DSSE specification follows semantic versioning, and is released using Git
tags. The `master` branch points to the latest release. Changes to the
specification are submitted against the `devel` branch, and are merged into
`master` when they are ready to be released.
