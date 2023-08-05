
import contextlib
import io
import pathlib
import sys
import unittest

from encrypted_config.crypto import encrypt
from encrypted_config.main import main
from .test_setup import run_module

_HERE = pathlib.Path(__file__).parent

if sys.version_info < (3, 5):

    class _RedirectStream:

        _stream = None

        def __init__(self, new_target):
            self._new_target = new_target
            self._old_targets = []

        def __enter__(self):
            self._old_targets.append(getattr(sys, self._stream))
            setattr(sys, self._stream, self._new_target)
            return self._new_target

        def __exit__(self, exctype, excinst, exctb):
            setattr(sys, self._stream, self._old_targets.pop())

    class _RedirectStderr(_RedirectStream):  # pylint: disable=too-few-public-methods

        _stream = 'stderr'

    contextlib.redirect_stderr = _RedirectStderr


class Tests(unittest.TestCase):

    def test_basic(self):
        sio = io.StringIO()
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stdout(sio):
                main(['-h'])
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stderr(sio):
                main(['test'])

    @unittest.expectedFailure
    def test_encrypt(self):
        public_key_path = pathlib.Path(_HERE, 'test_id_rsa.pub.pem')
        secret = encrypt('1234', public_key_path)
        sio = io.StringIO()
        with contextlib.redirect_stdout(sio):
            main(['encrypt', '--key', str(public_key_path),
                  '--json', '{"login": "1234"}', '--login'])
        self.assertIn('"secure:login": "{}"'.format(secret), sio.getvalue())

    def test_decrypt(self):
        public_key_path = pathlib.Path(_HERE, 'test_id_rsa.pub.pem')
        private_key_path = pathlib.Path(_HERE, 'test_id_rsa')
        secret = encrypt('1234', public_key_path)
        sio = io.StringIO()
        with contextlib.redirect_stdout(sio):
            main(['decrypt', '--key', str(private_key_path),
                  '--json', '{{"secure:login": "{}"}}'.format(secret)])
        self.assertIn('"login": "1234"', sio.getvalue())

    def test_as_script(self):
        sio = io.StringIO()
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stdout(sio):
                run_module('encrypted_config', '-h')
        run_module('encrypted_config', '-h', run_name='not_main')
