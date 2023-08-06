class String():

    def __init__(self, required=True, default=''):
        self.required = required
        self.default = default
        self.type = 'string'

    def __call__(self):
        return self.default


class List():

    def __init__(self, required=True, default=[]):
        self.required = required
        self.default = default
        self.type = 'list'

    def __call__(self):
        return self.default.copy()


class DocumentMetaclass(type):

    def __new__(cls, name, bases, dct):
        attrs = {}
        model = type.__new__(cls, name, bases, attrs)
        model.__init__ = cls.get_init(dct)
        model.format = cls.get_format(dct)
        model.fields = cls.get_fields(dct)
        return model

    @classmethod
    def get_format(cls, dct):
        @classmethod
        def callback(cls):
            rule_format = {}
            for attr_name, attr_value in dct.items():
                if isinstance(attr_value, (String, List)):
                    rule_format[attr_name] = {
                        'required': attr_value.required,
                        'type': attr_value.type}
            return rule_format
        return callback

    @classmethod
    def get_fields(cls, dct):
        @classmethod
        def callback(cls):
            return list(dct.keys())
        return callback

    @classmethod
    def get_init(cls, dct):
        def callback(self, *configs):
            for attr_name, attr_value in dct.items():
                if isinstance(attr_value, (String, List)):
                    setattr(self, attr_name, attr_value())

            for config in configs:
                for attr_name, attr_value in config.items():
                    if hasattr(self, attr_name):
                        if isinstance(attr_value, list):
                            old_attr = getattr(self, attr_name)
                            old_attr += attr_value
                            setattr(self, attr_name, old_attr)
                        elif isinstance(attr_value, str):
                            setattr(self, attr_name, attr_value)
        return callback


class Document(metaclass=DocumentMetaclass):
    output = String(required=False, default='output')
    template = String(required=False, default='')
    context = String(required=False, default='.')
    jars = List(required=False, default=[])
    metadata = List(required=False, default=[])
    toppings = List(required=False, default=[])
