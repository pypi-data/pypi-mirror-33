from os import makedirs

import json
from os.path import join, isfile, dirname
from typing import Callable, Any


class FitiWriter:
    def __init__(self, *path: str):
        self.filename = join(*path)
        makedirs(dirname(self.filename), exist_ok=True)

    def write(self, value: Any, modifier: Callable = lambda x: x):
        with open(self.filename, 'w') as f:
            f.write(modifier(value))

    def lines(self, value: list):
        return self.write(value or [], lambda x: '\n'.join(map(str, x)))

    def set(self, value: set):
        return self.write(value or set(), lambda x: '\n'.join(map(str, x)))

    def dict(self, value: dict):
        self.write(value or {}, json.dumps)

    def list(self, value: list):
        self.write(value or [], json.dumps)


class FitiReader:
    def __init__(self, *path: str):
        self.filename = join(*path)

    def read(self, default: Any = '', modifier: Callable = lambda x: x) -> Any:
        if not isfile(self.filename):
            return default
        with open(self.filename) as f:
            content = f.read()
        return modifier(content)

    def lines(self, typ: type = str) -> list:
        return self.read([], lambda x: [typ(i) for i in bool(x) * x.split('\n')])

    def set(self, typ: type = str) -> set:
        return self.read(set(), lambda x: {typ(i) for i in bool(x) * x.split('\n')})

    def dict(self) -> dict:
        return self.read({}, json.loads)

    def list(self) -> list:
        return self.read([], json.loads)


class Fitipy:
    def __init__(self, *path):
        self.path = join(*path)

    def read(self, *path: str) -> FitiReader:
        return FitiReader(self.path, *path)

    def write(self, *path: str) -> FitiWriter:
        return FitiWriter(self.path, *path)
