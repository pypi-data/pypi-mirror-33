"""The core configuration container class.
"""

from functools import singledispatch, wraps


class ConfigError(Exception):
    "Base class for kfg exceptions."
    pass


class ConfigKeyError(ConfigError, KeyError):
    """Indicates that a configuration key was not found."""
    pass


class ConfigValueError(ConfigError, ValueError):
    """Indicates that a configuration value was invalid."""
    pass


@singledispatch
def _normalize_key(key):
    """Put keys into normal, tuple form.
    """
    return key


@_normalize_key.register(str)
def _(key):
    """If the provided key is a simple string, we need to pack it into a 1-tuple.
    """
    return (key,)


def normalize_key(f):
    """Decorator that normalizes the key argument.

    This assumes that the key is the argument at index 1. In the future we
    might need to be smarter about normalizing the right argument, but for now
    this works.
    """
    @wraps(f)
    def wrapper(self, key, *args, **kwargs):
        return f(self, _normalize_key(key), *args, **kwargs)
    return wrapper


class Config:
    """A container for configuration data.

    kfg models configuration data as a tree structure of indexable objects. The
    top-level is always a dict, but intermediate objects could be lists,
    tuples, dicts, or anything else that can be indexed. Configuration values
    live at the leaves, and keys into the configuration are tuples of indices.

    The standard mapping operators, `[]` and `in`, work with `Config`s.

    Basic usage::

      >>> c = Config()
      >>> c['foo', 'bar'] = 42
      >>> ('foo', 'bar') in c
      True
      >>> c['foo', 'bar']
      42
      >>> c['important', 'data']
      ConfigKeyError

    Config also allows you to specify a "transform" for a key. This transform
    will be applied to the value at the key before it is provided to the user.
    If a transform fails (i.e. throws an exception) then a `ConfigValueError`
    will be generated. This helps you have validated configurations.

    """
    def __init__(self):
        "Create an empty Config."
        self._data = {}
        self._transforms = {}

    @normalize_key
    def __getitem__(self, key):
        """Get a configuration item by key.

        Args:
            key: The key of the value to get.

        Returns: The value at `key`.

        Raises:
            ConfigKeyError: If no value can be found at `key`.
            ConfigValueError: If the transform for the value (if any) fails.
        """
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
        """Set a config value.

        Args:
            key: The key of the value to set
            value: The value to set at `key`
        """
        level = self._data
        for segment in key[:-1]:
            if segment not in level:
                level[segment] = {}
            level = level[segment]
        level[key[-1]] = value

        # TODO: We should try to protect against invalid indexing, right?

    @normalize_key
    def __contains__(self, key):
        try:
            self[key]
            return True
        except ConfigKeyError:
            return False

    def get(self, key, default=None):
        """Get the value at `key`, or `default` if it doesn't exist.

        Args:
            key: The key to retrieve
            default: The value to return if `key` is not in the config.

        Returns: The value at `key`, or `default` if there is no value at `key`.
        """
        try:
            return self[key]
        except ConfigKeyError:
            return default

    DEFAULT_TRANSFORM_EXCEPTIONS = (ValueError,
                                    TypeError,
                                    KeyError,
                                    IndexError)

    @normalize_key
    def set_transform(self,
                      key,
                      transform,
                      exceptions=DEFAULT_TRANSFORM_EXCEPTIONS):
        """Set the transform for a key.

        The transform will be used to modify (or perhaps just validate) a value
        before it is passed back to callers.

        Config detects that a transform has failed by catching exceptions in
        the `exceptions` container. That is, if the transformation raises any
        exception in `exceptions`, then that exception is converted into a
        `ConfigValueError`. Any other exception is ignored and propagates up to
        the caller.

        Args:
            key: The key to which the transform applies.
            transform: a 1-argument callable that should return the transformed
                value for `key` or raise an exception.
            exceptions: Container of exception types which the transform will detect.

        """
        self._transforms[tuple(key)] = (transform, exceptions)

    def _apply_transform(self, key, value):
        """A apply a transform if it exists.
        """
        if key in self._transforms:
            transform, exceptions = self._transforms[key]
            try:
                value = transform(value)
            except exceptions as e:
                raise ConfigValueError() from e

        return value
