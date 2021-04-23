r"""Reference implementation of signing-spec.

Copyright 2021 Google LLC.
SPDX-License-Identifier: Apache-2.0

The following example requires `pip3 install pycryptodome` and uses ecdsa.py in
the same directory as this file.

>>> import binascii, os, sys, textwrap
>>> from pprint import pprint
>>> sys.path.insert(0, os.path.dirname(__file__))
>>> import ecdsa

>>> signer = ecdsa.Signer.construct(
...     curve='P-256',
...     d=97358161215184420915383655311931858321456579547487070936769975997791359926199,
...     point_x=46950820868899156662930047687818585632848591499744589407958293238635476079160,
...     point_y=5640078356564379163099075877009565129882514886557779369047442380624545832820)
>>> verifier = ecdsa.Verifier(signer.public_key)
>>> payloadType = 'http://example.com/HelloWorld'
>>> payload = b'hello world'

Signing example:

>>> signature_json = Sign(payloadType, payload, signer)
>>> pprint(json.loads(signature_json))
{'payload': 'aGVsbG8gd29ybGQ=',
 'payloadType': 'http://example.com/HelloWorld',
 'signatures': [{'sig': 'Cc3RkvYsLhlaFVd+d6FPx4ZClhqW4ZT0rnCYAfv6/ckoGdwT7g/blWNpOBuL/tZhRiVFaglOGTU8GEjm4aEaNA=='}]}

Verification example:

>>> result = Verify(signature_json, [('mykey', verifier)])
>>> pprint(result)
VerifiedPayload(payloadType='http://example.com/HelloWorld', payload=b'hello world', recognizedSigners=['mykey'])

PAE:

>>> def print_hex(b: bytes):
...   octets = ' '.join(textwrap.wrap(binascii.hexlify(b).decode('utf-8'), 2))
...   print(*textwrap.wrap(octets, 48), sep='\n')
>>> print_hex(PAE(payloadType, payload))
02 00 00 00 00 00 00 00 1d 00 00 00 00 00 00 00
68 74 74 70 3a 2f 2f 65 78 61 6d 70 6c 65 2e 63
6f 6d 2f 48 65 6c 6c 6f 57 6f 72 6c 64 0b 00 00
00 00 00 00 00 68 65 6c 6c 6f 20 77 6f 72 6c 64
"""

import base64, binascii, dataclasses, json, struct

# Protocol requires Python 3.8+.
from typing import Iterable, List, Protocol, Tuple


class Signer(Protocol):
    def sign(self, message: bytes) -> bytes:
        """Returns the signature of `message`."""
        ...


class Verifier(Protocol):
    def verify(self, message: bytes, signature: bytes) -> bool:
        """Returns true if `message` was signed by `signature`."""
        ...


# Collection of verifiers, each of which is associated with a name.
VerifierList = Iterable[Tuple[str, Verifier]]


@dataclasses.dataclass
class VerifiedPayload:
    payloadType: str
    payload: bytes
    recognizedSigners: List[str]  # List of names of signers


def b64enc(m: bytes) -> str:
    return base64.standard_b64encode(m).decode('utf-8')


def b64dec(m: str) -> bytes:
    m = m.encode('utf-8')
    try:
        return base64.b64decode(m, validate=True)
    except binascii.Error:
        return base64.b64decode(m, altchars='-_', validate=True)


def PAE(payloadType: str, payload: bytes) -> bytes:
    return b''.join([
        struct.pack('<Q', 2),
        struct.pack('<Q', len(payloadType)),
        payloadType.encode('utf-8'),
        struct.pack('<Q', len(payload)), payload
    ])


def Sign(payloadType: str, payload: bytes, signer: Signer) -> str:
    return json.dumps({
        'payload':
        b64enc(payload),
        'payloadType':
        payloadType,
        'signatures': [{
            'sig': b64enc(signer.sign(PAE(payloadType, payload)))
        }],
    })


def Verify(json_signature: str, verifiers: VerifierList) -> VerifiedPayload:
    wrapper = json.loads(json_signature)
    payloadType = wrapper['payloadType']
    payload = b64dec(wrapper['payload'])
    pae = PAE(payloadType, payload)
    recognizedSigners = []
    for signature in wrapper['signatures']:
        for name, verifier in verifiers:
            if verifier.verify(pae, b64dec(signature['sig'])):
                recognizedSigners.append(name)
    if not recognizedSigners:
        raise ValueError('No valid signature found')
    return VerifiedPayload(payloadType, payload, recognizedSigners)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
