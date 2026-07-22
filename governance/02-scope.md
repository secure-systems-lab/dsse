# DSSE Specification Scope

This document defines the strict boundaries of the Dead Simple Signing Envelope (DSSE) specification. By aggressively limiting its scope, DSSE provides a predictable, unambiguous cryptographic component designed to integrate safely into broader software supply chain frameworks and automated tooling architectures.

## 1. In Scope

The DSSE specification strictly defines the following mechanisms:

*   **Pre-Authentication Encoding (PAE):** A deterministic serialization format that securely binds a payload's data to its type definition before cryptographic signing. This ensures that signatures cannot be transplanted across different metadata types.
*   **Logical Envelope Structure:** A uniform conceptual wrapper that encapsulates the payload, its defined type descriptor, and one or more signatures. 
*   **Signature Object Schema:** The definition of each entry in the signature set, comprising the signature value and an optional key identifier that serves as a non-authoritative hint for selecting a verification key. This schema is the designated extension point for any additional signature-level fields.
*   **Multi-Signer Support:** Native architectural support for appending multiple independent signatures to the exact same payload without invalidating existing signatures or requiring nested envelopes.

## 2. Out of Scope

To eliminate parser vulnerabilities, mitigate cross-protocol attacks, and reduce integration friction, the following are explicitly out of scope for DSSE:

*   **Payload Canonicalization:** DSSE treats all payloads as opaque byte sequences (typically base64-encoded in text formats). Normalization or canonicalization of the payload structure (e.g., JSON Canonicalization Scheme) is deliberately omitted to prevent parser-level exploits prior to signature verification.
*   **Encryption and Confidentiality:** DSSE provides authentication and integrity only. It does not define or support mechanisms for payload encryption, privacy, or data masking.
*   **Cryptographic Algorithm Negotiation:** The envelope does not carry self-describing algorithm headers (for example, declaring whether ECDSA or Ed25519 was used), and it defines no mechanism for negotiating algorithms between signer and verifier. Where the signature schema carries fields that approximate algorithm or key identification, such as the optional key identifier, those fields are hints for key selection only. Verifiers are expected to determine the applicable algorithms out-of-band from the established trust root or verification policy.
*   **Key Management and Identity Binding:** Trust establishment, PKI, certificate validation, and key distribution are left to external systems (such as Sigstore, SPIFFE, or local policy engines).
*   **Payload Semantics:** DSSE makes no assertions about the internal validity, schema, or semantic meaning of the payload itself. It only guarantees that a specific entity signed a specific sequence of bytes under a declared payload type.

## 3. Component Interoperability

By maintaining these rigid boundaries, DSSE is designed to serve as a discrete, highly verifiable node within larger system architectures. It acts as a standardized interface for attestation and provenance data, allowing independent components and tools across the software supply chain to map, exchange, and verify signed metadata without requiring deep knowledge of the underlying payload structures.

DSSE is also independent of any particular serialization or transport. While it is most often represented in JSON for web-based APIs, the logical envelope structure and the PAE mechanism are format-agnostic: an implementation may serialize DSSE using Protocol Buffers, CBOR, XML, or any other structured data format, provided the defined envelope fields are preserved. This independence is a property of the design rather than a component the specification defines, which is why it is described here rather than in Section 1.

Any changes of Scope are not retroactive.
