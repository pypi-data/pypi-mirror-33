
import itertools
import logging
import pathlib
import unittest

import rsa

from encrypted_config.crypto import encrypt, decrypt

_LOG = logging.getLogger(__name__)

_HERE = pathlib.Path(__file__).parent


class Tests(unittest.TestCase):

    def test_encrypt_decrypt(self):
        public_key_path = pathlib.Path(_HERE, 'test_id_rsa.pub.pem')
        with public_key_path.open() as public_key_file:
            public_key_str = public_key_file.read()
        public_key = rsa.PublicKey.load_pkcs1(public_key_str, format='PEM')
        self.assertIsInstance(public_key, rsa.PublicKey)
        _LOG.info('using public key: %s', public_key_path)

        private_key_path = pathlib.Path(_HERE, 'test_id_rsa')
        with private_key_path.open() as private_key_file:
            private_key_str = private_key_file.read()
        private_key = rsa.PrivateKey.load_pkcs1(private_key_str, format='PEM')
        self.assertIsInstance(private_key, rsa.PrivateKey)
        _LOG.info('using private key: %s', private_key_path)

        for public_, private_ in itertools.product(
                (public_key_path, public_key_str, public_key),
                (private_key_path, private_key_str, private_key)):
            for example in ('1234', b'1234'):
                ciphertext = encrypt(example, public_)
                self.assertIsInstance(ciphertext, type(example))
                cleartext = decrypt(ciphertext, private_)
                self.assertEqual(cleartext, example)
