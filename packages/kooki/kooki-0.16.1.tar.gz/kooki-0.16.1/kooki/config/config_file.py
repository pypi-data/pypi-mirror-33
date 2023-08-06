import os, yaml, textwrap

from ..exception import KookiException


class NoConfigFileFound(KookiException):

    message = textwrap.dedent('''\
        No '{}' file found.
        Create one by executing 'kooki new'.''')

    def __init__(self, config_file_name):
        message = self.message.format(config_file_name)
        super().__init__(message)


class YamlErrorConfigFileParsing(KookiException):

    message = textwrap.dedent('''\
        Yaml error during config file parsing.
        Please check the format of your config file.''')

    def __init__(self, exc):
        message = self.message
        super().__init__(message)


class YamlErrorConfigFileBadType(KookiException):

    message = textwrap.dedent('''\
        The Yaml parsed should be a dict and it is a {}.
        Please check the format of your config file.''')

    def __init__(self, type_found):
        message = self.message.format(type_found)
        super().__init__(message)


def read_config_file(config_file_name):
    if os.path.isfile(config_file_name):
        with open(config_file_name, 'r') as stream:
            try:
                content = stream.read()
                config = yaml.safe_load(content)
                if not isinstance(config, dict):
                    raise YamlErrorConfigFileBadType(type(config))
                return config
            except yaml.YAMLError as exc:
                raise YamlErrorConfigFileParsing(exc)
    else:
        raise NoConfigFileFound(config_file_name)
