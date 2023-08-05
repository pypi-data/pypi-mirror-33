"""Transforming JSON."""

import abc
import typing as t


class JSONTransformer(metaclass=abc.ABCMeta):

    """Transform JSON."""

    def __init__(self):
        pass

    def transform(self, data: t.Any) -> t.Any:
        transformed_data = self.transform_value(data)
        return transformed_data

    def transform_value(self, data: t.Union[str, list, dict]) -> t.Union[str, list, dict]:
        if isinstance(data, str):
            return self.transform_str(data)
        if isinstance(data, list):
            return self.transform_list(data)
        if isinstance(data, dict):
            return self.transform_dict(data)
        return data

    @abc.abstractmethod
    def transform_dict(self, data: dict) -> dict:
        assert isinstance(data, dict), type(data)
        return data

    @abc.abstractmethod
    def transform_list(self, data: list) -> list:
        assert isinstance(data, list), type(data)
        return data

    @abc.abstractmethod
    def transform_str(self, data: str) -> str:
        assert isinstance(data, str), type(data)
        return data
