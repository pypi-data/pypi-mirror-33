class StyleVariable:
    def __init__(self):
        self.value = None

    def __call__(self, value):
        self.value = value
        return self

    def __str__(self):
        return str(self.value)


class StyleVariableStorage:
    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]
        else:
            self.__dict__[item] = StyleVariable()
            return self.__dict__[item]

    def __setattr__(self, key, value):
        if key in self.__dict__:
            self.__dict__[key](value)
        else:
            self.__dict__[key] = StyleVariable()
            self.__dict__[key](value)


class Style(dict):
    def __init__(self):
        self.variable = StyleVariableStorage()

    def __str__(self):
        out = ''
        for selector, attributes in self.items():
            out += selector + ' {' + '; '.join(f'{k.replace("_", "-")}: {v}' for k, v in attributes.items()) + ';} '
            # out += selector + ' {\n\t' + ';\n\t'.join(f'{k.replace("_", "-")}: {v}' for k, v in attributes.items()) + ';\n}\n\n'
        return out

    def list_variables(self):
        return [x for x in dir(self.variable) if not x.startswith('_')]