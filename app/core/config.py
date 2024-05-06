from kp_py.api.conf.configuration import ConfigurationBase


class Config(ConfigurationBase):

    def __init__(self, paths):
        ConfigurationBase.__init__(self, allow_missing_files=True)
        self.shortcut_url = self.config.get_env(
            env_var='SHORTCUT_URL',
            fallback='https://api.app.shortcut.com/api/v3'
        )
        self.shortcut_token = self.config.get_env(env_var='SHORTCUT_TOKEN')

        self.log_level = self.config.get_env(env_var='LOG_LEVEL', fallback='WARNING')
        self.version = self.read_version()
