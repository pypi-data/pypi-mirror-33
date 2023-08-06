import importlib
import os
import sys
from contextlib import contextmanager

from ajelastic.exceptions import AJElasticSettingsError

_REQUIRED_SETTINGS = [
    "ES_HOST",
    "ES_ENV"
]


@contextmanager
def cwd_in_path():
    cwd = os.getcwd()
    if cwd in sys.path:
        yield
    else:
        sys.path.insert(0, cwd)
        try:
            yield cwd
        finally:
            try:
                sys.path.remove(cwd)
            except ValueError:  # pragma: no cover
                pass


def load_settings():
    """
    First checks whether the consuming project is Django project or not (i.e., if DJANGO_SETTINGS_MODULE env is
    specified or not) else reads the project settings path specified in AJ_ELASTIC_CONF env variable.
    :return: Settings object
    """
    try:
        setting_path = os.environ["DJANGO_SETTINGS_MODULE"]
    except KeyError:
        try:
            setting_path = os.environ["AJ_ELASTIC_CONF"]
        except KeyError:
            raise AJElasticSettingsError("Missing env AJ_ELASTIC_CONF")
    with cwd_in_path():
        settings = importlib.import_module(setting_path)
    settings_missing = []
    for _ in _REQUIRED_SETTINGS:
        if not hasattr(settings, _):
            settings_missing.append(_)
    if not settings_missing:
        return settings
    # Throw error
    raise AJElasticSettingsError("Missing required settings {}".format(",".join(settings_missing)))
