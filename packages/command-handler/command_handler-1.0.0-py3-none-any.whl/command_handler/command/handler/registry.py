from re import compile, escape

from .exceptions import HandlerAlreadyExistsException


class Registry():
    def __init__(self):
        self.storage = {}

    def add(self, command, handler, schema):
        if command in self:
            raise HandlerAlreadyExistsException
        self.storage[command] = (handler, schema)

    def __contains__(self, needle):
        key = self.resolveKey(needle)

        return key in self.storage

    def __getitem__(self, needle):
        return self.storage[self.resolveKey(needle)]

    def resolveKey(self, needle):
        for key in self.storage:
            if not self.isKeyMatching(needle, self.keyToRegex(key)):
                continue
            return key

        return needle

    def isKeyMatching(self, key, regex):
        return regex.match(key) is not None

    def keyToRegex(self, key):
        rKey = escape(key) \
            .replace("\\.\\#", "(\\..+|)") \
            .replace("\\*", "[^\\.]+")
        pattern = "^" + rKey + "$"

        return compile(pattern)


registry = Registry()
