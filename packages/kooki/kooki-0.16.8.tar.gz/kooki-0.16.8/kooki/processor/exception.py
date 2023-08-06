import textwrap
import yaml

from ..exception import KookiException


class MissingJar(KookiException):

    message = textwrap.dedent('''\
        Cannot find jar '{}'.
        Is it installed ? Try to run kooki bake with --update.
        Please check the jar of your config file.''')

    def __init__(self, jar):
        message = self.message.format(jar)
        super().__init__(message)


class MissingResource(KookiException):

    message = textwrap.dedent('''\
        Cannot find {0} '{1}' in the following directory:
        {2}
        Please check the {0} of your config file.''')

    def __init__(self, jars, resource_name, resource):
        from .jars import get_search_paths
        directories = get_search_paths(jars)
        directories_str = '\n'.join(['- {}'.format(directory) for directory in directories])
        message = self.message.format(resource_name, resource, directories_str)
        super().__init__(message)


class MissingFile(MissingResource):

    def __init__(self, jars, file_path):
        super().__init__(jars, 'template', file_path)


class MissingTemplate(MissingResource):

    def __init__(self, jars, template):
        super().__init__(jars, 'template', template)


class MissingMetadata(MissingResource):

    def __init__(self, jars, metadata):
        super().__init__(jars, 'metadata', metadata)


class MissingContent(MissingResource):

    def __init__(self, jars, content):
        super().__init__(jars, 'content', content)


class TooMuchResult(KookiException):

    message = textwrap.dedent('''\
        Too much files match the name provided ({})
        {}
        You should provide the full name with the file extension.''')

    def __init__(self, name, result):
        message = self.message.format(name, yaml.dump(result, default_flow_style=False)[:-1])
        super().__init__(message)


class ErrorEvaluatingExpression(KookiException):

    def __init__(self, expression, message):
        super().__init__('')
        self.expression = []
        self.path = []
        self.message = message
        self.expression.append(expression)

    def add_expression(self, expression):
        self.expression.append(expression)

    def add_path(self, path):
        self.path.append(path)

    def __str__(self):
        message = ''
        for expression, path in zip(self.expression, self.path):
            message += expression
            message += ' in ' + path
            message += '\n'
        message += self.message
        return message
