import functools

class Foo:

    @property
    def badprop(self):
        raise AttributeError

    def __getattr__(self, item):
        return "I am %s" % item

