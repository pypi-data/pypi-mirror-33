from typing import Dict
from enum import Enum


from .query_key import QueryKey


class Keywords:
    EXPAND = '__expand__'


def need_expand(v):
    if not isinstance(v, dict):
        return False
    if Keywords.EXPAND in v:
        return v[Keywords.EXPAND]
    return True


from collections import UserDict


class CNode(UserDict):
    class KEYS:
        NO_EXPAND = '_no_expand_'

    def __init__(self, data=None, father=None):
        """
        Args:
            `data`: dict or CNode.
        """
        self.data = {}
        if data is None:
            data = {}
        if isinstance(data, dict):
            for k, v in data.items():
                self._update_kernel(k, v)
        elif isinstance(data, CNode):
            self.data = data.data
        else:
            raise TypeError("data {} is not convertable")
        self.father = father

    def _update_kernel(self, key, value):
        if not isinstance(value, dict) or value.get(self.KEYS.NO_EXPAND):
            self.data[key] = value
        else:
            self.data[key] = CNode(value, self)

    def __setitem__(self, key, value):
        self._update_kernel(key, value)

    def read(self, key: QueryKey, default_value=None):
        """
        Find value curresponding to key.
        if len(key) == 1, then find it in self._values,
        else find it in self._children recuresivly.
        """
        key = QueryKey(key)
        if len(key) == 0:
            return self
        if len(key) == 1:
            return self.get(key.head())
        if not key.head() in self.data or not isinstance(
                self.data[key.head()], CNode):
            return default_value
        return self.data.get(key.head()).read(key.tail())

    @property
    def children(self):
        return {k: v for k, v in self.data.items() if isinstance(v, CNode)}

    def create(self, key: QueryKey, node_or_value):
        """
        Create a new child node or value.
        """
        return self.update(key, node_or_value, allow_exist=False)

    def is_ancestor_of(self, n):
        for k, v in self.data.items():
            if not isinstance(v, CNode):
                continue
            if v is n or v.is_ancestor_of(n):
                return True
        return False

    def update(self,
               key: QueryKey,
               node_or_value,
               *,
               allow_exist=True,
               overwrite_node=False):
        """
        Updating config.
        If node_or_value is a value, update directly.
        If node_or_value is a CNode, check if this node exists.
            If not exists: direct assign.
            If exists: update each item of that node. 
        Note: the node_or_value argument is not assigned to the node tree.
        """
        key = QueryKey(key)
        if len(key) == 0:
            if not isinstance(node_or_value, (dict, CNode)):
                raise ValueError(
                    "Can not update node with none CNode object or dict, overrite_node might need to be True."
                )
            for k, v in node_or_value.items():
                if isinstance(self.data.get(k), CNode):
                    self.data[k].update(v)
                else:
                    self.data[k] = v
            return self
        if key.head() in self.data and not allow_exist:
            raise ValueError("Key {} alread existed.".format(key.head()))
        if len(key) > 1:
            if not isinstance(self.data.get(key.head()),
                              CNode) or overwrite_node:
                self.data[key.head()] = CNode().update(key.tail(),
                                                       node_or_value)
            else:
                self.data[key.head()].update(key.tail(), node_or_value)
            return self
        if len(key) == 1:
            if not isinstance(self.data.get(key.head()),
                              CNode) or overwrite_node:
                if need_expand(node_or_value):
                    self.data[key.head()] = from_dict(node_or_value)
                else:
                    self.data[key.head()] = node_or_value
            else:
                self.data[key.head()].update([], node_or_value)
            return self


def from_dict(config_dict):
    return CNode(config_dict)


class DefaultConfig:
    _current = None

    def __init__(self, cnode):
        pass

    @property
    def node(self):
        return self._current

    def __enter__(self):
        pass


class CNodeRoot(CNode):
    pass
