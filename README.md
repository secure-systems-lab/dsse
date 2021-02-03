# signing-spec

Simple, foolproof standard for signing arbitrary data.

*   Why not [JOSE/JWS/JWT](https://jwt.io)? JSON-specific, too complicated, too
    easy to mess up.
*   Why not [PASETO](https://paseto.io)? JSON-specific, too opinionated.

## What is it?

*   [Signature protocol](specification.md)
*   [Data structure](specification.md) for storing the message and signatures
*   (pending #9) Suggested crypto primitives

Out of scope (for now at least):

*   Key management / PKI

## Who uses it?

*   [in-toto](https://in-toto.io) (pending in-toto/ITE#13)
*   [TUF](https://theupdateframework.io) (pending)
