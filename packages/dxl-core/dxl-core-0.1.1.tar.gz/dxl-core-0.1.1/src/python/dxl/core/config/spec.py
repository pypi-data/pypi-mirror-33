from .view import CView


class Specs(CView):
    FIELDS = tuple()

    # def __init__(self, root, path):
    #     self.data = {k: v for k, v in config.items()
    #                  if k in self.FIELDS}

    def __getattr__(self, key):
        if key in self.FIELDS:
            return self.data[key]
        raise KeyError("Key {} not found.".format(key))
