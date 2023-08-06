"""
Settings and configuration for Aasaanjobs Elasticsearch

Values will be read from the module specified by the AJELASTIC_SETTINGS_MODULE environment variable or
DJANGO_SETTINGS_MODULE if a Django project (in that order).
"""
import importlib
import os
import sys
from contextlib import contextmanager

import lazy_object_proxy

from ajelastic.exceptions import AJElasticSettingsError


ENVIRONMENT_VARIABLE = "AJELASTIC_SETTINGS_MODULE"
DJANGO_ENVIRONMENT_VARIABLE = "DJANGO_SETTINGS_MODULE"


def _setup():
    """
    Load the settings module pointed to by the environment variable.
    """
    settings_module = os.environ[ENVIRONMENT_VARIABLE] \
        if os.environ.get(ENVIRONMENT_VARIABLE) else os.environ.get(DJANGO_ENVIRONMENT_VARIABLE)
    if not settings_module:
        raise AJElasticSettingsError(
            "Settings are not configured. "
            "You must define one of the environment variables {} or {}."
            .format(ENVIRONMENT_VARIABLE, DJANGO_ENVIRONMENT_VARIABLE)
        )
    return Settings(settings_module)


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


class BaseSettings(object):
    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)


class EsIndices:
    pass


class Settings(BaseSettings):
    _mandatory_settings = (
        "ES_HOST", "ES_ENV"
    )

    def __init__(self, settings_module):
        with cwd_in_path():
            mod = importlib.import_module(settings_module)
        self.settings_module = settings_module
        for setting in dir(mod):
            if setting.isupper() and setting.startswith("ES_"):
                setting_value = getattr(mod, setting)
                setattr(self, setting, setting_value)
        self.validate()
        self.ES_INDICES = self.init_es_indices()

    def validate(self):
        for setting in self._mandatory_settings:
            if not getattr(self, setting):
                raise AJElasticSettingsError("The {} setting must not be empty.".format(setting))
        self.validate_es_indices()

    @staticmethod
    def validate_es_index(key: str, setting: dict):
        _mandatory_fields = ("name", "doc_type")
        for _ in _mandatory_fields:
            if not setting.get(_):
                raise AJElasticSettingsError("The {}.{} setting must not be empty.".format(key, _))
        allowed_fields = _mandatory_fields + ("data_functions", "mapping_path")
        for _ in setting.keys():
            if _ not in allowed_fields:
                raise AJElasticSettingsError("Unknown {}.{} setting provided.".format(key, _))

    def validate_es_indices(self):
        if not hasattr(self, "ES_INDICES"):
            return
        if not isinstance(self.ES_INDICES, dict):
            raise AJElasticSettingsError("The ES_INDICES setting must be a dict.")
        for key, value in self.ES_INDICES.items():
            self.validate_es_index(key, value)

    def init_es_indices(self):
        if not hasattr(self, "ES_INDICES"):
            return None
        indices = EsIndices()
        for key, value in self.ES_INDICES.items():
            from ..definition import ElasticIndex
            setattr(indices, key, ElasticIndex.from_dict(self.ES_ENV, key, value))
        return indices

    def __repr__(self):
        return "<AJElasticSettings {}".format(self.settings_module)


settings = lazy_object_proxy.Proxy(_setup)
