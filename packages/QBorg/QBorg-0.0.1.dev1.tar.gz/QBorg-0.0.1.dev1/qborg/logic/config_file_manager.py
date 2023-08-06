import io
import fcntl
import os
import yaml

from qborg.entities.config import Config


class ConfigFileManager:
    CONFIG_FILE_LOCATIONS = (os.path.join(os.path.expanduser('~'), '.config', 'qborg', 'config.yaml'),)

    @classmethod
    def _find_config(cls, config_file=None):
        # Check if passed config file exists
        if config_file:
            if not os.path.isfile(config_file):
                raise ConfigFileError('Passed config file does not exist.', config_file)
            return config_file

        # If no config file was passed fall back to default locations
        for loc in cls.CONFIG_FILE_LOCATIONS:
            if os.path.isfile(loc):
                return loc

        return cls.CONFIG_FILE_LOCATIONS[0]

    def __init__(self, config_file=None):
        self._config = Config()
        self._config_path = ConfigFileManager._find_config(config_file)

        if os.path.isfile(self._config_path):
            self._config_file = open(self._config_path, 'r+')
            self.load_config()

    def __del__(self):
        if hasattr(self, '_config_file') and self._config_file:
            fcntl.flock(self._config_file, fcntl.LOCK_UN)
            self._config_file.close()

    @property
    def path(self):
        return self._config_path

    @property
    def config(self):
        return self._config

    def load_config(self):
        if not hasattr(self, '_config_file') or not self._config_file:
            raise ConfigFileError('No config file specified')

        fcntl.flock(self._config_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self._config_file.seek(0, io.SEEK_SET)
        yaml_config = yaml.load(self._config_file)

        if not yaml_config:
            raise ConfigFileError('Config file is empty', self._config_path)

        self._config = Config.load(yaml_config)

    def save_config(self):
        if not hasattr(self, '_config_file') or not self._config_file:
            print('Creating config file %s...' % self._config_path)
            os.makedirs(os.path.abspath(os.path.dirname(self._config_path)), exist_ok=True)
            open(self._config_path, 'a').close()
            self._config_file = open(self._config_path, 'r+')

        _dumper = yaml.dumper.SafeDumper
        _dumper.ignore_aliases = lambda self, data: True

        self._config_file.seek(0)
        self._config_file.truncate(0)
        yaml.dump(self._config.dump(), self._config_file,
                  Dumper=_dumper, default_flow_style=False)


class ConfigFileError(Exception):
    def __init__(self, message, path=None):
        super().__init__(message)
        self.message = message
        self.config_path = path

    def __str__(self):
        if self.config_path:
            return 'Error with config file %s: %s ' % (self.config_path, self.message)
        else:
            return self.message
