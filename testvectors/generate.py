r"""Generate the DSSE test vectors in vectors.json.

Requires `pip3 install pycryptodome`. Ed25519 signatures are deterministic, so
running this script reproduces vectors.json byte for byte:

    python3 testvectors/generate.py            # rewrite vectors.json
    python3 testvectors/generate.py --check    # exit 1 if vectors.json differs

The two signing keys are the RFC 8032 section 7.1 TEST 1 and TEST 2 keys, so
anyone can check them against the RFC.
"""

import base64, json, os, sys

from Crypto.PublicKey import ECC
from Crypto.Signature import eddsa

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'vectors.json')

SEEDS = {
    'A': '9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60',
    'B': '4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb',
}
INTOTO = 'application/vnd.in-toto+json'
STATEMENT = b'{"_type":"https://in-toto.io/Statement/v1"}'


def PAE(payload_type: str, payload: bytes) -> bytes:
    t = payload_type.encode('utf-8')
    return b'DSSEv1 %d %b %d %b' % (len(t), t, len(payload), payload)


def key(name):
    return ECC.construct(curve='Ed25519', seed=bytes.fromhex(SEEDS[name]))


def public_hex(name):
    return key(name).public_key().export_key(format='raw').hex()


def sign(name, payload_type, payload):
    return eddsa.new(key(name), 'rfc8032').sign(PAE(payload_type, payload))


def b64(m, urlsafe=False):
    enc = base64.urlsafe_b64encode if urlsafe else base64.standard_b64encode
    return enc(m).decode('ascii')


def envelope(payload_type, payload, sigs, urlsafe=False):
    return {
        'payload': b64(payload, urlsafe),
        'payloadType': payload_type,
        'signatures': [
            dict({'sig': b64(s, urlsafe)}, **({'keyid': k} if k else {}))
            for k, s in sigs
        ],
    }


def vector(vid, description, env, signed_type, signed_payload, keys, threshold,
           supported, expect):
    return {
        'id': vid,
        'description': description,
        'envelope': env,
        'trustedKeys': keys,
        'threshold': threshold,
        'supportedPayloadTypes': supported,
        'pae': PAE(signed_type, signed_payload).hex(),
        'expect': expect,
    }


def build():
    sa = sign('A', INTOTO, STATEMENT)
    sb = sign('B', INTOTO, STATEMENT)
    binary = bytes([0xfb, 0xff, 0xbf, 0x3e, 0x3f])
    s_bin = sign('A', INTOTO, binary)
    utype = 'application/vnd.exämple+json'
    s_utf = sign('A', utype, STATEMENT)
    s_empty = sign('A', INTOTO, b'')
    s_notype = sign('A', '', STATEMENT)
    vectors = [
        vector('single-signature',
               'One signature by a trusted key over the PAE of the payload.',
               envelope(INTOTO, STATEMENT, [('A', sa)]), INTOTO, STATEMENT,
               ['A'], 1, [INTOTO], 'accept'),
        vector('url-safe-base64',
               'Payload and signature in URL-safe base64; verifiers MUST accept either alphabet.',
               envelope(INTOTO, binary, [('A', s_bin)], urlsafe=True), INTOTO, binary,
               ['A'], 1, [INTOTO], 'accept'),
        vector('payload-type-swapped',
               'The signature covers application/vnd.in-toto+json, but the envelope claims another type.',
               envelope('application/vnd.example.other+json', STATEMENT, [('A', sa)]),
               INTOTO, STATEMENT, ['A'], 1, [INTOTO, 'application/vnd.example.other+json'],
               'reject'),
        vector('non-ascii-payload-type',
               'LEN(type) is the byte length of UTF8(PAYLOAD_TYPE), 29 here, not the 28 characters.',
               envelope(utype, STATEMENT, [('A', s_utf)]), utype, STATEMENT,
               ['A'], 1, [utype], 'accept'),
        vector('empty-payload',
               'An empty SERIALIZED_BODY is signed as "... 0 " with a trailing space.',
               envelope(INTOTO, b'', [('A', s_empty)]), INTOTO, b'',
               ['A'], 1, [INTOTO], 'accept'),
        vector('empty-payload-type',
               'A valid signature over an empty PAYLOAD_TYPE, which no verifier supports.',
               envelope('', STATEMENT, [('A', s_notype)]), '', STATEMENT,
               ['A'], 1, [INTOTO], 'reject'),
        vector('threshold-two-distinct-keys',
               'Two signatures by two different trusted keys meet a threshold of two.',
               envelope(INTOTO, STATEMENT, [('A', sa), ('B', sb)]), INTOTO, STATEMENT,
               ['A', 'B'], 2, [INTOTO], 'accept'),
        vector('threshold-two-one-key-twice',
               'The same key signs twice; one unique key does not meet a threshold of two.',
               envelope(INTOTO, STATEMENT, [('A', sa), ('A', sa)]), INTOTO, STATEMENT,
               ['A', 'B'], 2, [INTOTO], 'reject'),
        vector('threshold-two-without-keyids',
               'KEYID is optional: two distinct signers that omit it still meet a threshold of two.',
               envelope(INTOTO, STATEMENT, [(None, sa), (None, sb)]), INTOTO, STATEMENT,
               ['A', 'B'], 2, [INTOTO], 'accept'),
    ]
    return {
        'description': 'DSSE protocol test vectors. See README.md in this directory.',
        'keys': {n: {'algorithm': 'ed25519', 'seed': SEEDS[n], 'public': public_hex(n)}
                 for n in sorted(SEEDS)},
        'vectors': vectors,
    }


def main():
    text = json.dumps(build(), indent=2, ensure_ascii=False) + '\n'
    if '--check' in sys.argv[1:]:
        with open(OUT, encoding='utf-8') as f:
            if f.read() != text:
                print('vectors.json differs from what generate.py produces')
                return 1
        print('vectors.json matches')
        return 0
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(text)
    return 0


if __name__ == '__main__':
    sys.exit(main())
