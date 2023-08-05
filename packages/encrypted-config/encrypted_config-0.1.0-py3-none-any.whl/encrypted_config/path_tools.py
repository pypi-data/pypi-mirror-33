
import os
import pathlib
import typing as t


def normalize_path(path: t.Union[pathlib.Path, str]) -> t.Union[pathlib.Path, str]:
    if isinstance(path, str):
        return os.path.expanduser(os.path.expandvars(path))
    return pathlib.Path(normalize_path(str(path)))
