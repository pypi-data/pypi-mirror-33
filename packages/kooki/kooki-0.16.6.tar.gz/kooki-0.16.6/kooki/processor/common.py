import empy, os
import pretty_output

from collections import OrderedDict

from kooki.tools import get_front_matter, write_file

from .metadata import Metadata
from .exception import ErrorEvaluatingExpression


def export_to(name, extension, content):
    file_name = '{0}{1}'.format(name, extension)
    write_file(file_name, content)
    absolute_path = os.path.join(os.getcwd(), file_name)
    return absolute_path


def apply_template(data, metadata):
    result = ''
    front_matter, content = get_front_matter(data)
    unique_metadata = get_metadata(front_matter, metadata)
    result = apply_interpreter(content, unique_metadata)
    return result


def get_metadata(front_matter, metadata):
    metadata_copy = Metadata()
    metadata_copy.update(front_matter)
    metadata_copy.update(metadata)
    return metadata_copy


def apply_interpreter(content, metadata):
    interpreter = empy.Interpreter()
    interpreter.setPrefix('@')
    result = interpreter.expand(content, metadata)
    return result