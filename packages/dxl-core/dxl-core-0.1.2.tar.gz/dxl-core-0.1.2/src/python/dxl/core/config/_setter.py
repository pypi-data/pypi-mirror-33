from typing import Dict, Any


class ConfigScope:
    pass


def load_config_from_file(path: str) -> Dict[str, Any]:
    import json
    import yaml
    with open(path) as fin:
        if path.endswith('.yml'):
            return yaml.load(fin)
        elif path.endswith('.json'):
            return json.load(fin)


def load_config_in_workdirectory(filename):
    pass


def load_config_in_user_config(filename, default_root=None):
    pass


"""
c = cfg.get_module_config(__name__)
with cfg.ConfigScope():

"""
