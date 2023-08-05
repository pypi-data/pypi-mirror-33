
import base64
import pathlib
import typing as t

import rsa


def prepare_public_key(public_key: t.Union[pathlib.Path, str, rsa.PublicKey]) -> rsa.PublicKey:
    if isinstance(public_key, pathlib.Path):
        with public_key.open() as key_file:
            public_key = key_file.read()
    if isinstance(public_key, str):
        # if public_key.startswith('ssh-rsa '):
        #    public_key = openssh_public_key_to_pem(public_key)
        public_key = rsa.PublicKey.load_pkcs1(public_key, format='PEM')
    assert isinstance(public_key, rsa.PublicKey), type(public_key)
    return public_key


def encrypt(data: t.Union[str, bytes],
            public_key: t.Union[pathlib.Path, str, rsa.PublicKey]) -> t.Union[str, bytes]:
    """Encrypt given data using the given RSA public key."""
    return_base64 = False
    if isinstance(data, str):
        data = data.encode('utf-8')
        return_base64 = True
    assert isinstance(data, bytes), type(data)
    public_key = prepare_public_key(public_key)
    encrypted_data = rsa.encrypt(data, public_key)
    if return_base64:
        encrypted_data = base64.b64encode(encrypted_data).decode('ascii')
    return encrypted_data


def prepare_private_key(private_key: t.Union[pathlib.Path, str, rsa.PrivateKey]) -> rsa.PrivateKey:
    if isinstance(private_key, pathlib.Path):
        with private_key.open() as key_file:
            private_key = key_file.read()
    if isinstance(private_key, str):
        private_key = rsa.PrivateKey.load_pkcs1(private_key, format='PEM')
    assert isinstance(private_key, rsa.PrivateKey), type(private_key)
    return private_key


def decrypt(data: t.Union[str, bytes],
            private_key: t.Union[pathlib.Path, str, rsa.PrivateKey]) -> t.Union[str, bytes]:
    """Decrypt given data using the given RSA private key."""
    return_bytes = True
    if isinstance(data, str):
        data = base64.b64decode(data.encode('ascii'))
        return_bytes = False
    private_key = prepare_private_key(private_key)
    decrypted_data = rsa.decrypt(data, private_key)
    if not return_bytes:
        decrypted_data = decrypted_data.decode('utf-8')
    return decrypted_data
