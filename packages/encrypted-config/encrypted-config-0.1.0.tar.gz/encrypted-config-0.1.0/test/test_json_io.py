
# import logging
import pathlib
import tempfile
import unittest

from encrypted_config.json_io import json_to_str, str_to_json, json_to_file, file_to_json

# _LOG = logging.getLogger(__name__)

# _HERE = pathlib.Path(__file__).parent

EXAMPLES = {
    '""': "", '"1234"': "1234",
    '[]': [], '[\n  "1234"\n]': ["1234"],
    r'{}': {}, '{\n  "key": 1\n}': {"key": 1}}

BAD_EXAMPLE = '["1234", "1234]'


class Tests(unittest.TestCase):

    def test_str(self):
        for example_str, example in EXAMPLES.items():
            result_str = json_to_str(example)
            self.assertEqual(example_str, result_str)
            result = str_to_json(example_str)
            self.assertEqual(example, result)

        with self.assertRaises(ValueError):
            str_to_json(BAD_EXAMPLE)

    def test_file(self):
        for _, example in EXAMPLES.items():
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                path = pathlib.Path(tmp.name)
            json_to_file(example, path)
            result = file_to_json(path)
            path.unlink()
            self.assertEqual(example, result)

        with tempfile.NamedTemporaryFile('w', delete=False) as tmp:
            tmp.write(BAD_EXAMPLE)
            path = pathlib.Path(tmp.name)
        with self.assertRaises(ValueError):
            file_to_json(path)
        path.unlink()
