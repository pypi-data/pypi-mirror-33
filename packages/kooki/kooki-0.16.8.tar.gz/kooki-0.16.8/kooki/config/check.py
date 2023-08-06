from cerberus import Validator
from .document import Document

document_format = Document.format()
document_fields = Document.fields()

document_version_1 = {
    **document_format,
    'default': {
        'required': False,
        'type': 'dict',
        'excludes': document_fields,
        'dependencies': 'kooki',
        'schema': document_format
    },
    'kooki': {
        'required': False,
        'type': 'dict',
        'excludes': document_fields,
        'keyschema': {'type': 'string', 'regex': '[A-Za-z0-9_]+'},
        'valueschema': {
            'required': False,
            'type': 'dict',
            'schema': document_format
        }
    }
}


def check_config_format(config):
    v = Validator(document_version_1)
    config_valid = v.validate(config, document_version_1)
    if not config_valid:
        raise Exception(v.errors)
