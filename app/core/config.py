import os

from app.core.envconfigparser import EnvConfigParser


class Config(object):
    """Configuration base with singleton."""

    _config = None

    def __init__(self, paths=None):
        if paths is None:
            paths = []
        self.config = EnvConfigParser()
        env_cfg_path = os.environ.get('SHORTCUT_API_CFG')
        if env_cfg_path:
            paths.append(env_cfg_path)
        self.config.read(paths)
        self.shortcut_url = self.config.get_env(
            env_var='SHORTCUT_URL',
            fallback='https://api.app.shortcut.com/api/v3'
        )
        self.shortcut_token = self.config.get_env(env_var='SHORTCUT_TOKEN')
        self.log_level = self.config.get_env(env_var='LOG_LEVEL', fallback='WARNING')
        self.version = self.read_version()

    @classmethod
    def get_config(cls, paths=None):
        if cls._config is None or paths:
            cls._config = cls(paths)
        return cls._config

    @classmethod
    def read_version(cls):
        try:
            fh = open('version.txt', 'r')
            value = '\n'.join(fh.readlines()).rstrip()
            fh.close()
            return value
        except EnvironmentError:
            return 'missing'
