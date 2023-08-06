import yaml

from kfg.config import Config


def load_config(stream, config=None):
    """Load a YAML configuration from a file-like object.

    If `config` is not `None`, then it will be used to hold the loaded
    configuration information; all data in the instance will be replaced.
    Otherwise, a new instance of `Config` will be created, populated, and
    returned.

    Args:
      config: An instance of `Config`, or `None`. The data in this instance will be replaced.

    Returns: An instance of `Config`.

    Raises:
      ValueError: If there is an error loading the config.
    """

    if config is None:
        config = Config()

    try:
        data = yaml.safe_load(stream)
        config._data = data
        return config
    except (UnicodeDecodeError, yaml.parser.ParserError) as exc:
        raise ValueError(
            'Error loading configuration from {}'.format(stream)) from exc


def serialize_config(config):
    """Convert a `Config` into a string.

    This is complementary with `load_config`.
    """
    return yaml.dump(config._data)
