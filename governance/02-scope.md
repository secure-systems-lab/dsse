# DSSE Specification Scope

This document defines the strict boundaries of the Dead Simple Signing Envelope (DSSE) specification. By aggressively limiting its scope, DSSE provides a predictable, unambiguous cryptographic component designed to integrate safely into broader software supply chain frameworks and automated tooling architectures.

## 1. In Scope

The DSSE specification strictly defines the following mechanisms:

*   **Pre-Authentication Encoding (PAE):** A deterministic serialization format that securely binds a payload's data to its type definition before cryptographic signing. This ensures that signatures cannot be transplanted across different metadata types.
*   **Logical Envelope Structure:** A uniform conceptual wrapper that encapsulates the payload, its defined type descriptor, and one or more signatures. 
*   **Format and Transport Agnosticism:** While frequently represented in JSON for web-based APIs, the DSSE logical structure and PAE mechanism are entirely format-agnostic. DSSE can be natively serialized using Protocol Buffers, CBOR, XML, or any other structured data format, provided the core envelope fields are preserved.
*   **Multi-Signer Support:** Native architectural support for appending multiple independent signatures (and their respective key identifiers) to the exact same payload without invalidating existing signatures or requiring nested envelopes.

## 2. Out of Scope

To eliminate parser vulnerabilities, mitigate cross-protocol attacks, and reduce integration friction, the following are explicitly out of scope for DSSE:

*   **Payload Canonicalization:** DSSE treats all payloads as opaque byte sequences (typically base64-encoded in text formats). Normalization or canonicalization of the payload structure (e.g., JSON Canonicalization Scheme) is deliberately omitted to prevent parser-level exploits prior to signature verification.
*   **Encryption and Confidentiality:** DSSE provides authentication and integrity only. It does not define or support mechanisms for payload encryption, privacy, or data masking.
*   **Cryptographic Algorithm Negotiation:** The envelope intentionally omits self-describing cryptographic algorithm headers (e.g., specifying whether ECDSA or Ed25519 was used). Verifiers are expected to determine the correct algorithms out-of-band based on the established trust root or key identifier.
*   **Key Management and Identity Binding:** Trust establishment, PKI, certificate validation, and key distribution are left to external systems (such as Sigstore, SPIFFE, or local policy engines).
*   **Payload Semantics:** DSSE makes no assertions about the internal validity, schema, or semantic meaning of the payload itself. It only guarantees that a specific entity signed a specific sequence of bytes under a declared payload type.

## 3. Component Interoperability

By maintaining these rigid boundaries, DSSE is designed to serve as a discrete, highly verifiable node within larger system architectures. It acts as a standardized interface for attestation and provenance data, allowing independent components and tools across the software supply chain to map, exchange, and verify signed metadata without requiring deep knowledge of the underlying payload structures.
