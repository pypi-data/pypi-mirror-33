import os
import pretty_output

from kooki.tools import get_front_matter, read_file

from .common import apply_template
from .metadata import Metadata
from .renderer import render
from .exception import ErrorEvaluatingExpression


def load_extensions(document, template_extension):
    loader = ExtensionLoader(document, template_extension)
    loader.load()
    return loader.extensions


class ExtensionLoader():

    def __init__(self, document, template_extension):
        self.document = document
        self.template_extension = template_extension
        self.extensions = Metadata()

    def load(self):
        self.load_jars()
        self.load_locals()

    def load_locals(self):
        path = os.path.join(os.getcwd(), self.document.context)
        self.load_directory(path)

    def load_jars(self):
        for path in self.document.jars:
            self.load_directory(path)

    def load_directory(self, directory, prefix=[]):
        for element in os.listdir(directory):
            path = os.path.join(directory, element)
            if os.path.isdir(path):
                self.load_directory(path, prefix=[*prefix, element])

            elif os.path.isfile(path):
                root, ext = os.path.splitext(element)
                if ext in ['.md', self.template_extension]:
                    self.add(root, ext, path, prefix)

    def add(self, name, ext, path, prefix):
        tmp = self.extensions
        for prefix_part in prefix:
            if prefix_part not in tmp:
                tmp[prefix_part] = Metadata()
            tmp = tmp[prefix_part]
        tmp[name] = self.create(name, path, ext)

    def create(self, name, file_full_path, ext):
        extension = Extension(self.document, name, file_full_path, ext)
        return extension


class Extension():

    level = 0

    def __init__(self, document, name, path, template_extension):
        self.document = document
        self.name = name
        self.path = path
        self.template_extension = template_extension
        file_content = read_file(path)
        self.front_matter, self.content = get_front_matter(file_content)

    def __call__(self, *args, **kwargs):
        try:


            metadata_copy = Metadata()
            metadata_copy.update(self.front_matter)
            metadata_copy.update(self.document.metadata)
            new_args = {}
            for index, arg in enumerate(args):
                new_args['arg{}'.format(index)] = arg
            metadata_copy.update(**new_args)
            metadata_copy.update(**kwargs)
            content = self.content

            pretty_output.debug_on()
            if Extension.level == 0:
                pretty_output.colored(self.name, 'white', 'on_yellow')
            else:
                message = ''
                for i in range(0, self.level-1):
                    message += '│   '
                message += '├'
                message += '─' * 2
                message += ' '
                pretty_output.colored(message, 'white', 'on_yellow', end='')
                pretty_output.colored(self.name, 'white', 'on_yellow')
            Extension.level += 1
            char = '└'
            pretty_output.debug_off()

            if self.template_extension == '.md':
                content = render(content, self.document.metadata)

            content = apply_template(content, metadata_copy)

            Extension.level -= 1

            return content

        except ErrorEvaluatingExpression as e:
            e.add_path(self.path)
            raise e