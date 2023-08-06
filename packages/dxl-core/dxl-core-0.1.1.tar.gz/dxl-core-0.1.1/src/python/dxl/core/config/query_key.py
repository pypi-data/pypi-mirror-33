class QueryKey:
    """
    <Immutable>
    """

    def __init__(self, key=None):
        if isinstance(key, QueryKey):
            self.data = key.data
        elif isinstance(key, str):
            self.data = self.parse_str(key)
        elif key is None:
            self.data = ()
        elif isinstance(key, (list, tuple)):
            self.data = tuple(key)
        else:
            raise TypeError(
                "Key {} is not convertable to QueryKey.".format(key))

    def head(self):
        if len(self.data) == 0:
            return None
        return self.data[0]

    def tail(self):
        return QueryKey(self.data[1:])

    def last(self):
        if len(self.data) == 0:
            return None
        return self.data[-1]

    def __len__(self):
        return len(self.data)

    def __eq__(self, q):
        return self.data == QueryKey(q).data

    def get_query(self, dct):
        for k in self.data:
            dct = dct[k]
        return dct

    def set_query(self, dct, value):
        if len(self.data) < 1:
            raise ValueError("Set query requires len(key) >= 1.")
        for k in self.data[:-1]:
            v = dct.get(k)
            if v is None:
                dct[k] = {}
            dct = v
        dct[self.data[-1]] = value

    @classmethod
    def parse_str(self, key):
        return key.split('/')