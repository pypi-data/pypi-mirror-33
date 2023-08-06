from dxl.fs import Path

from pathlib import Path
from .cnode import QueryKey, CNode


def _parse_query_key(key: str, parse_dot=True):
    if parse_dot:
        for i, v in enumerate(key):
            if i == 0:
                continue
            if i == len(key) - 1:
                continue
            if v != '.':
                continue
            if key[i - 1] == '/' or key[i + 1] == '/':
                continue
            key[i] = '/'
    kp = Path(key)
    if str(kp) == '/':
        return QueryKey([])
    return QueryKey(kp.parts)


def _find_ancestors(root, cnode):
    result = []
    current = root
    found = True
    while current.is_ancestor_of(cnode):
        result.append(current)
        found = False
        for _, v in current.children.items():
            if v.is_ancestor_of(cnode):
                current = v
                found = True
                break
        if not found:
            break
    return tuple(result)


def base_node(root, key_path):
    result = root.read(_parse_query_key(key_path))
    if result is None:
        raise ValueError("No node of {} is found.".format(key_path))
        # root.update(_parse_query_key(key_path), CNode())
        # result = root.read(_parse_query_key(key_path))
    return result


class CView:
    """
    Viewer of CNode.
    Provide simplified hierarchy access to values.
    """

    def __init__(self, root, base=None):
        if isinstance(root, dict):
            root = CNode(root)
            base = root
        elif isinstance(root, CView):
            root = root.root
            if base is None:
                base = root.base

        self._root = root
        if base is None:
            self._base = root
        else:
            self._base = base

    @property
    def root(self):
        return self._root

    @property
    def base(self):
        return self._base

    def get_kernel(self, key, value=None):
        v = self._base.read(_parse_query_key(key))
        if isinstance(v, CNode):
            return CView(self._root, v)
        if v is None:
            return value
        return v

    def search(self, key):
        v = self.get_kernel(key)
        if v is not None:
            return v
        acs = _find_ancestors(self._root, self._base)
        for n in reversed(acs):
            v = CView(self._root, n).search(key)
            if v is not None:
                return v
        return v

    def __getitem__(self, key):
        return self.search(key)

    def get(self, key, value=None):
        v = self.search(key)
        if v is None:
            return value
        return v

    def items(self):
        return self._base.items()


def create_view(root, key_path):
    """
    Get config view by path
    """
    return CView(root, base_node(root, key_path))


# class ConfigViewer:
#     def __unified_keys(self, path_or_keys):
#         if isinstance(path_or_keys, (list, tuple)):
#             return list(self.base.parts()), list(path_or_keys)
#         else:
#             return list(self.base.parts()), list(Path(path_or_keys).parts())

#     def _get_value_raw(self, keys):
#         result = self.data
#         for k in keys:
#             if not isinstance(result, (dict, ConfigsView)):
#                 return None
#             result = result.get(k)
#         return result

#     def _form_path(self, keys):
#         return '/'.join(keys)

#     def _query(self, base_keys, local_keys):
#         # if len(local_keys) <= 1:
#         result = self._get_value_raw(base_keys + local_keys)
#         # else:
#         # path = self.base / local_keys[0]
#         # key_path = self._form_path(local_keys[1:])
#         # result = ConfigsView(self.data, path)._query(key_path)
#         return result

#     def _search(self, key):
#         base_keys, local_keys = self.__unified_keys(key)
#         result = self._query(base_keys, local_keys)
#         path = self._form_path(base_keys + local_keys)
#         if result is None and len(base_keys) > 0:
#             new_path = self._form_path((base_keys + local_keys)[:-2])
#             result, _ = ConfigsView(self.data, new_path)._search(
#                 local_keys[-1])
#         return result, path

#     def _post_processing(self, result, path, default, restrict):
#         if isinstance(result, dict) or (result is None and default is None
#                                         and not restrict):
#             result = ConfigsView(self.data, path)
#         elif result is None:
#             result = default
#         return result

#     def to_dict(self):
#         result, path = self._search(str(self.base))
#         if isinstance(result, dict):
#             return result
#         else:
#             raise ValueError("Configs view on base path is not dict.")

#     def get(self, key, default=None, *, restrict=False):
#         result, path = self._search(key)
#         return self._post_processing(result, path, default, restrict)

#     def __getitem__(self, key):
#         return self.get(key, restrict=True)

#     def __iter__(self):
#         dct = self._get_value_raw(self.base.parts())
#         if dct is None:
#             return list().__iter__()
#         else:
#             return dct.__iter__()

# def view(path_like_key, config=None):
#     pass

# def child_view(configs_view, extend_path):
#     return ConfigsView(configs_view.base_path / str(extend_path),
#                        configs_view.data)
