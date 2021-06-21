"""Example crypto implementation: ECDSA with deterministic-rfc6979 and SHA256.

Copyright 2021 Google LLC.
SPDX-License-Identifier: Apache-2.0
"""

from Crypto.Hash import SHA256
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS


class Signer:
    def __init__(self, secret_key):
        self.secret_key = secret_key
        self.public_key = self.secret_key.public_key()

    @classmethod
    def construct(cls, *, curve, d, point_x, point_y):
        return cls(
            ECC.construct(curve=curve, d=d, point_x=point_x, point_y=point_y))

    @classmethod
    def generate(cls, *, curve, randfunc=None):
        return cls(ECC.generate(curve=curve, randfunc=randfunc))

    def sign(self, message: bytes) -> bytes:
        """Returns the signature of `message`."""
        h = SHA256.new(message)
        return DSS.new(self.secret_key, 'deterministic-rfc6979').sign(h)

    def keyid(self) -> str:
        """Returns a fingerprint of the public key."""
        return Verifier(self.public_key).keyid()


class Verifier:
    def __init__(self, public_key):
        self.public_key = public_key

    def verify(self, message: bytes, signature: bytes) -> bool:
        """Returns true if `message` was signed by `signature`."""
        h = SHA256.new(message)
        try:
            DSS.new(self.public_key, 'fips-186-3').verify(h, signature)
            return True
        except ValueError:
            return False

    def keyid(self) -> str:
        """Returns a fingerprint of the public key."""
        # Note: This is a hack for demonstration purposes. A proper fingerprint
        # should be used.
        key = self.public_key.export_key(format='OpenSSH').encode('ascii')
        return SHA256.new(key).hexdigest()[:8]
