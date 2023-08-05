"""Encrypting and decrypting JSON."""

import pathlib
import typing as t

import rsa

from .json_transform import JSONTransformer
from .crypto import prepare_public_key, encrypt, prepare_private_key, decrypt


class JSONEncrypter(JSONTransformer):

    """Encrypt JSON."""

    def __init__(self, public_key: t.Union[pathlib.Path, str, rsa.PublicKey], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._public_key = prepare_public_key(public_key)  # type: rsa.PublicKey

    def transform_dict(self, data: dict) -> dict:
        data = super().transform_dict(data)
        raise NotImplementedError()

    def transform_list(self, data: list) -> list:
        data = super().transform_list(data)
        raise NotImplementedError()

    def transform_str(self, data: str) -> str:
        data = super().transform_str(data)
        return 'secure:{}'.format(encrypt(data, self._public_key))


def encrypt_json(data: t.Union[str, list, dict],
                 public_key: t.Union[pathlib.Path, str, rsa.PublicKey],
                 *args, **kwargs) -> t.Union[str, list, dict]:
    encrypter = JSONEncrypter(public_key, *args, **kwargs)
    return encrypter.transform(data)


class JSONDecrypter(JSONTransformer):

    """Decrypt JSON."""

    def __init__(self, private_key: t.Union[pathlib.Path, str, rsa.PublicKey], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._private_key = prepare_private_key(private_key)  # type: rsa.PrivateKey
        self.keep_encrypted = True

    def transform_dict(self, data: dict) -> dict:
        data = super().transform_dict(data)
        transformed = type(data)()
        for key, value in data.items():
            if key.startswith('secure:'):
                transformed[key[7:]] = decrypt(value, self._private_key)
            if not key.startswith('secure:') or self.keep_encrypted:
                transformed[key] = value
        return transformed

    def transform_list(self, data: list) -> list:
        data = super().transform_list(data)
        transformed = type(data)()
        for value in data:
            if value.startswith('secure:'):
                transformed.append(decrypt(value[7:], self._private_key))
            else:
                transformed.append(value)
        return transformed

    def transform_str(self, data: str) -> str:
        if data.startswith('secure:'):
            return decrypt(data[7:], self._private_key)
        return data


def decrypt_json(data: t.Union[str, list, dict],
                 private_key: t.Union[pathlib.Path, str, rsa.PublicKey],
                 *args, **kwargs) -> t.Union[str, list, dict]:
    """Create decrypted JSON object from a partially encryted file or JSON object."""
    decrypter = JSONDecrypter(private_key, *args, **kwargs)
    return decrypter.transform(data)
