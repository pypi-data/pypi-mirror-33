import re


class ZcyMethod:

    def __init__(self, name, signature):
        self.name = name
        self.signature = '' if signature is None else signature

    def get_invoke_str(self):
        method_name = self.name
        method_signature = '({})'.format(self.signature) if re.match(r'^\(.*\)$', self.signature) is None \
            else self.signature
        return method_name + method_signature
