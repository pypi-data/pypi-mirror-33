import yaml, os, textwrap

from codecs import open

from .exception import KookiException


def get_front_matter(content):
    first_line = content.split('\n', 1)[0]
    front_matter = {}

    if first_line == '---':
        content_splitted = content.split('---\n')
        if len(content_splitted) >= 3:
            metadata_content = content_splitted[1]
            content = '---\n'.join(content_splitted[2:])
            front_matter = yaml.load(metadata_content)
        else:
            content = '---\n'.join(content_splitted)

    return front_matter, content


def read_file(file_name):
    try:
        stream = open(file_name, 'r', encoding='utf8')
        content = stream.read()
    except IOError as e:
        raise RuntimeError('No such file: \'{0}\''.format(file_name))
    else:
        stream.close()
        return content


def write_file(file_name, content):
    path = '/'.join(file_name.split('/')[:-1])
    if path != '' and not os.path.isdir(path):
        os.makedirs(path)

    stream = open(file_name, 'w', encoding='utf8')
    stream.write(content)
    stream.close()
    return content


def read_config_file(config_file_name, must_exist=False):
    if os.path.isfile(config_file_name):
        content = read_file(config_file_name)
        try:
            config = yaml.safe_load(content)
            if not isinstance(config, dict):
                raise YamlErrorConfigFileBadType(type(config))
            return config
        except yaml.YAMLError as exc:
            raise YamlErrorConfigFileParsing(exc)
    else:
        if must_exist:
            raise NoConfigFileFound(config_file_name)


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