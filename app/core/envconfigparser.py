# -*- coding: utf-8 -*-

"""
Subclass to ConfigParser with methods that first look in environment variables
for values overriding the config file settings.

Given a config file
[section]
option=value

The call get_env*(env_var='ENV_VAR', section='section', option='option', fallback='fallback')
will return in descending order (if the former are missing or None):
 * The contents of the file pointed to by environment variable 'ENV_VAR_FILE'
 * The contents of environment variable 'ENV_VAR'
 * "value1"
 * or if the config file is changed and section/option doesn't exist: "fallback"

You can skip the env_var parameter by setting a parameter prefix and letting the
environment parameter names
follow the naming pattern  "prefix_section_option" in upper case, e.g.

config.set_prefix('KP_INVOICEAPI')
host = config.get_env(section='Api', option='host')

will read the environment variable KP_INVOICEAPI_API_HOST

Overridden values are persisted to the config object, but not written to the underlying file.
If the original config values are needed, read the file again.



"""
import configparser
import os
from io import StringIO


def get_env_var(variable_name, default_value=None):
    filename = os.environ.get(variable_name + "_FILE", None)
    if filename:
        try:
            fh = open(filename, 'r')
            value = '\n'.join(fh.readlines()).rstrip()
            fh.close()
            return value
        except EnvironmentError:
            pass
    return os.environ.get(variable_name, default_value)


class EnvConfigParserException(BaseException):
    pass


class EnvConfigParser(configparser.ConfigParser):
    def __init__(self):
        configparser.ConfigParser.__init__(self)
        self.prefix = ""
        self.secret_config_settings = set()
        self.env_vars = dict()

    def set_env_prefix(self, prefix):
        self.prefix = prefix.upper()

    def set_hidden(self, *, env_var=None, section=None, option=None):
        if (not env_var) and (not section):
            raise EnvConfigParserException('Need to specify either section and option OR env_var')
        if env_var:
            self.secret_config_settings.add((env_var,))
        if section:
            if not option:
                option = ''
            self.secret_config_settings.add((section.lower(), option.lower()))

    def set_safe(self, *, section, option, env_var, value):
        if value is None:
            return
        if section:
            if not self.has_section(section):
                self.add_section(section)
            self.set(section=section, option=option, value=str(value))
        if env_var:
            self.env_vars[env_var] = str(value)

    def get_env(self, section=None, option=None, env_var=None,
                fallback=None, hidden=False, required=False):
        """ Get config option but look at environment variables first """
        if (not env_var) and not (section and option):
            raise EnvConfigParserException('Need to specify either section and option OR env_var')
        if hidden:
            self.set_hidden(env_var=env_var,
                            section=section, option=option)
        if env_var is None:
            env_var = f'{self.prefix}_{section.upper()}_{option.upper()}'
        result = self.env_vars.get(env_var,
                                   get_env_var(env_var, None))

        if result is None and section:
            if self.has_option(section, option):
                result = self.get(section, option)

        if result is None:
            if required:
                raise EnvConfigParserException('Required configuration setting missing: '
                                               f'section: {section or "-"} '
                                               f'option: {option or "-"} '
                                               f'env_var: {env_var or "-"}')
            result = fallback
        self.set_safe(section=section, option=option, value=result, env_var=env_var)
        return result

    def get_env_boolean(self, section=None, option=None, env_var=None, fallback=None, hidden=False,
                        required=False):
        result = self.get_env(section, option, env_var=env_var, fallback=fallback,
                              hidden=hidden, required=required)
        try:
            value = self._convert_to_boolean(result)
        except AttributeError:
            value = self.BOOLEAN_STATES[str(result).lower()]
        self.set_safe(section=section, option=option, value=result, env_var=env_var)
        return value

    def get_env_float(self, section=None, option=None, env_var=None, fallback=None,
                      hidden=False, required=False):
        return float(self.get_env(env_var=env_var, section=section, option=option,
                                  fallback=fallback, hidden=hidden, required=required))

    def get_env_int(self, section=None, option=None, env_var=None, fallback=None, hidden=False,
                    required=False):
        return int(self.get_env(env_var=env_var, section=section, option=option,
                                fallback=fallback, hidden=hidden, required=required))

    def __str__(self):
        c = self
        if self.secret_config_settings:
            c = EnvConfigParser()
            for sec in self.sections():
                for (name, value) in self.items(sec):
                    if (sec.lower(), name.lower()) not in self.secret_config_settings \
                            and (sec.lower(), '') not in self.secret_config_settings:
                        if not c.has_section(sec):
                            c.add_section(sec)
                        c.set(sec, name, value)
        sio = StringIO()
        c.write(sio)
        s = sio.getvalue()
        sio.close()
        return s
