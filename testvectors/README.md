# DSSE test vectors

`vectors.json` holds test vectors for the [protocol](../protocol.md). Each vector
is an envelope, the verifier configuration to check it with, and the expected
result.

| Field | Meaning |
| ----- | ------- |
| `envelope` | The envelope, in the [JSON envelope](../envelope.md) format. |
| `trustedKeys` | Names of the keys in `keys` that the verifier trusts. |
| `threshold` | The number of unique trusted keys that must verify a signature. |
| `supportedPayloadTypes` | The payload types the verifier supports. |
| `pae` | Hex of `PAE(UTF8(PAYLOAD_TYPE), SERIALIZED_BODY)` that the signatures cover. |
| `expect` | `accept` or `reject`. |

The keys are Ed25519 keys from [RFC 8032, section 7.1](https://www.rfc-editor.org/rfc/rfc8032#section-7.1)
(TEST 1 and TEST 2), so the signatures are deterministic.

To regenerate the file and to check an implementation, install `pycryptodome`, then run
these commands from the repository root:

```shell
python3 testvectors/generate.py --check    # vectors.json matches the generator
python3 testvectors/check_reference.py     # the reference implementation passes every vector
```
