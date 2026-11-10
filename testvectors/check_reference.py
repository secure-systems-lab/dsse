r"""Run vectors.json against the reference implementation in ../implementation.

Requires `pip3 install pycryptodome`. Exits 1 if any vector gets the wrong result.

    python3 testvectors/check_reference.py

The reference Verify() returns every recognized signer and leaves the threshold
and the payload-type check to its caller, so this harness applies both: a
vector is accepted when Verify() succeeds, the payload type is supported, and
the number of unique recognized signers meets the vector's threshold.
"""

import json, os, sys

from Crypto.Signature import eddsa

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'implementation'))
import signing_spec  # noqa: E402


class Ed25519Verifier:
    def __init__(self, name, public_hex):
        self.name = name
        self.key = eddsa.import_public_key(bytes.fromhex(public_hex))

    def verify(self, message, signature):
        try:
            eddsa.new(self.key, 'rfc8032').verify(message, signature)
            return True
        except ValueError:
            return False

    def keyid(self):
        return self.name


def outcome(vector, keys):
    verifiers = [(n, Ed25519Verifier(n, keys[n]['public'])) for n in vector['trustedKeys']]
    env = vector['envelope']
    try:
        result = signing_spec.Verify(json.dumps(env), verifiers)
    except ValueError:
        return 'reject'
    if env['payloadType'] not in vector['supportedPayloadTypes']:
        return 'reject'
    if len(set(result.recognizedSigners)) < vector['threshold']:
        return 'reject'
    return 'accept'


def main():
    with open(os.path.join(HERE, 'vectors.json'), encoding='utf-8') as f:
        data = json.load(f)
    failed = 0
    for vector in data['vectors']:
        got = outcome(vector, data['keys'])
        env = vector['envelope']
        pae = signing_spec.PAE(env['payloadType'], signing_spec.b64dec(env['payload'])).hex()
        pae_ok = vector['expect'] == 'reject' or pae == vector['pae']
        ok = got == vector['expect'] and pae_ok
        failed += not ok
        print('%s %s: expected %s, got %s%s' % ('ok  ' if ok else 'FAIL', vector['id'],
              vector['expect'], got, '' if pae_ok else ', PAE differs'))
    print('%d of %d vectors failed' % (failed, len(data['vectors'])))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
