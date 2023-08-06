from typing import Dict, Any
import os
import yaml


ConfigDict = Dict[str, Any]


class ConfigFile:
    def __init__(self, filename: str, fail: bool = False) -> None:
        self.filename = filename
        self.fail = fail


class Config:
    DEFAULT_FILES = (
        ConfigFile('config/default.yml', fail=False),
        ConfigFile('config/local.yml', fail=False))

    def __init__(self, config: ConfigDict = None) -> None:
        self._config = config or {}

    def read_all(self, filename: str = None):
        config_files = list(self.DEFAULT_FILES)
        if filename:
            config_files.append(ConfigFile(filename, fail=True))
        for config_file in config_files:
            self.read(config_file.filename, fail=config_file.fail)
        self.load_env()
        return self

    def read(self, filename: str, fail: bool = False):
        try:
            with open(filename) as file:
                self.load(file.read())
        except FileNotFoundError as e:
            if fail:
                raise e
        return self

    def load(self, yaml_contents: str):
        source: ConfigDict = yaml.safe_load(yaml_contents) or {}
        self.merge(source)
        return self

    def load_env(self, variable: str = 'CONFIG'):
        return self.load(os.getenv(variable, ''))

    def __getitem__(self, key: str):
        prop = self._config
        for _key in key.split('.'):
            try:
                prop = prop[_key]
            except KeyError:
                raise KeyError(
                    'Configuration roperty "{}" not defined'.format(key))
        return prop

    def _merge(self, source: ConfigDict, destination: ConfigDict):
        stack = [(source, destination)]

        while stack:
            src, dest = stack.pop()
            for key, value in src.items():
                if isinstance(value, dict):
                    if key not in dest or not isinstance(dest[key], dict):
                        dest[key] = {}
                    stack.append((value, dest[key]))
                    continue
                dest[key] = value

        return destination

    def merge(self, config: ConfigDict):
        self._merge(config, self._config)
        return self

    def __repr__(self):
        return 'Config[_config={}]'.format(self._config)
