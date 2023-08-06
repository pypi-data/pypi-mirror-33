import importlib
import json

from ajelastic.exceptions import AJElasticSettingsError


class ElasticDataFunctions:
    def __init__(self, **kwargs):
        self.single = kwargs.get("single")
        self.multi = kwargs.get("multi")

    @staticmethod
    def load_from_module(value: str):
        module, fn_name = value.split(":")
        if not module:
            raise ValueError
        if not fn_name:
            raise ValueError
        mod = importlib.import_module(module)
        return getattr(mod, fn_name)

    @classmethod
    def get_function(cls, key: str, value: str, context: str):
        if not value:
            return None
        try:
            return cls.load_from_module(value)
        except ValueError:
            raise AJElasticSettingsError(
                "The setting ES_INDICES.{}.{} is improperly configured. "
                "Should be of the form <module_name>:<function_name>"
                .format(context, key)
            )

    @classmethod
    def from_dict(cls, context: str, value: dict):
        if not value:
            return None
        return cls(
            single=cls.get_function("single", value.get("single"), context),
            multi=cls.get_function("multi", value.get("multi"), context)
        )


class ElasticIndex:
    def __init__(
        self,
        name: str,
        doc_type: str,
        es_env: str,
        data_fns: ElasticDataFunctions=None,
        mapping_path: str = None,
    ):
        self.index = "_".join([name, es_env])
        self.doc_type = doc_type
        self.data_fns = data_fns
        self.mapping = self.get_mapping(mapping_path) if mapping_path else None

    @staticmethod
    def get_mapping(path: str):
        """
        Reads JSON mapping from the file
        :param path: Absolute path to the mapping file
        :return: Elasticsearch mapping (in dict)
        """
        with open(path, "r") as fp:
            content = json.load(fp)
        return content

    @classmethod
    def from_dict(cls, es_env: str, context: str, values: dict):
        return cls(
            name=values["name"],
            doc_type=values["doc_type"],
            es_env=es_env,
            data_fns=ElasticDataFunctions.from_dict(
                context="{}.data_functions".format(context), value=values.get("data_functions")
            ),
            mapping_path=values.get("mapping_path")
        )
