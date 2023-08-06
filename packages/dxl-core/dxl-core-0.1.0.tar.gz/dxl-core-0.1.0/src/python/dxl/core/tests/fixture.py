from pathlib import Path

DEFAULT_PATH = '/gluster/share/develop/fixtures'


class PersistentFixturesManager:
    """
    Singleton. 
    """
    _path = None

    @classmethod
    def path(cls):
        """
        Root path of all fixture data.
        """
        return Path(cls._path)

    @classmethod
    def default_path(cls):
        return Path(DEFAULT_PATH)

    @classmethod
    def reset(cls):
        """
        Reset configs to its default value.
        """
        cls._path = cls.default_path()
