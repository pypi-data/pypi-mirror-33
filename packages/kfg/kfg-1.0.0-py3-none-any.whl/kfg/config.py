from functools import singledispatch, wraps


class ConfigError(Exception):
    pass


class ConfigKeyError(ConfigError, KeyError):
    """Indicates that a configuration key was not found."""
    pass


class ConfigValueError(ConfigError, ValueError):
    """Indicates that a configuration value was invalid."""
    pass


@singledispatch
def _normalize_key(key):
    return key


@_normalize_key.register(str)
def _(key):
    return (key,)


def normalize_key(f):
    @wraps(f)
    def wrapper(self, key, *args, **kwargs):
        return f(self, _normalize_key(key), *args, **kwargs)
    return wrapper


class Config:
    def __init__(self):
        self._data = {}
        self._transforms = {}

    @normalize_key
    def __getitem__(self, key):
        level = self._data
        try:
            for segment in key[:-1]:
                level = level[segment]

            value = level[key[-1]]
        except KeyError:
            raise ConfigKeyError(
                'No config entry at path {}'.format(
                    key))
        except TypeError:
            # Assumption is this is caused by indexing an un-indexable object.
            # Perhaps an explicit check above would be cleaner.
            raise ConfigKeyError(
                'No config entry at path {}'.format(
                    key))


        return self._apply_transform(key, value)

    @normalize_key
    def __setitem__(self, key, value):
        level = self._data
        for segment in key[:-1]:
            if segment not in level:
                level[segment] = {}
            level = level[segment]
        level[key[-1]] = value

    @normalize_key
    def __contains__(self, key):
        try:
            self[key]
            return True
        except ConfigKeyError:
            return False

    def get(self, key, default=None):
        try:
            return self[key]
        except ConfigKeyError:
            return default

    @normalize_key
    def set_transform(self, key, transform):
        self._transforms[tuple(key)] = transform

    def _apply_transform(self, key, value):
        if key in self._transforms:
            try:
                value = self._transforms[key](value)
            except (ValueError, TypeError, KeyError, IndexError) as e:
                raise ConfigValueError() from e
        return value
