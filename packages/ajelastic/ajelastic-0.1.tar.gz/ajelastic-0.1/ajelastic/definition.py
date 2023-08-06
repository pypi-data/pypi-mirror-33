from typing import Dict, Callable
import json


class ElasticDataFunctions:
    def __init__(self, **kwargs):
        self.single = kwargs.get("single")
        self.multi = kwargs.get("multi")


class ElasticIndex:
    def __init__(
        self,
        name: str,
        doc_type: str,
        data_fns: Dict[str, Callable]=dict,
        mapping_path: str = None
    ):
        self.index = name
        self.doc_type = doc_type
        self.data_fns = ElasticDataFunctions(
            single=data_fns.get("single"),
            multi=data_fns.get("multi")
        )
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
