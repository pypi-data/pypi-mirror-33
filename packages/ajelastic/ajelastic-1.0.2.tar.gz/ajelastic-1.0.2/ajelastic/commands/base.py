"""
Base Elasticsearch Indexing Command
"""
import argparse
from datetime import datetime
from time import time

from elasticsearch import Elasticsearch, ConflictError

from ajelastic.exceptions import AJElasticSettingsError
from ..conf import settings


class BaseElasticCommand:
    name = ""
    description = ""

    def __init__(self):
        assert self.name, "Missing name declaration."
        assert self.description, "Missing description declaration."
        if not settings.ES_INDICES:
            raise LookupError("Missing ES_INDICES settings.")
        parser = argparse.ArgumentParser(prog=self.name, description=self.description)
        parser.add_argument("entity", metavar="ENTITY", type=str, nargs=1,
                            help="Entity name as specified in ES_INDICES settings")
        parser.add_argument("batch_size", nargs="?", type=int, default=1000,
                            help="Object size of each bulk API request sent to elasticsearch")

        args = parser.parse_args()
        try:
            self.entity = getattr(settings.ES_INDICES, args.entity[0])
        except AttributeError:
            raise AJElasticSettingsError("The entity {} is not configured. Please fix your ES_INDICES settings".
                                         format(args.entity[0]))
        from ..definition import ElasticIndex
        assert isinstance(self.entity, ElasticIndex), "Invalid entity {}".format(args.entity)
        self.batch_size = args.batch_size
        self.es_client = Elasticsearch(settings.ES_HOST)

    def log(self, msg: str, msg_type: str = "INFO", end="\n"):
        print("[{}][{}] {} - {}".format(
            self.name,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            msg_type,
            msg
        ), end=end)

    def log_err(self, msg: str):
        self.log(msg, "**ERROR**")

    @property
    def index_alias(self):
        return self.entity.index

    @property
    def doc_type(self):
        return self.entity.doc_type

    def get_old_index(self):
        self.log("Attempting to find existing index for alias {}".format(self.index_alias))
        res = self.es_client.indices.get_alias(self.index_alias)
        if len(res) > 1:
            raise ConflictError("More than one indices with alias {} found.".format(self.index_alias))
        index = list(res.keys())[0]
        self.log("Found {}".format(index))

    def create_index(self):
        new_name = "{}_{}".format(self.index_alias, round(time()))
        self.log("Attempting to create new index {}".format(new_name))
        self.es_client.indices.create(index=new_name)
        self.log("Created new index {}".format(new_name))
        return new_name

    def delete_index(self, name):
        self.log("Attempting to delete index {}".format(name))
        self.es_client.indices.delete(index=name)
        self.log("Deleted index {}".format(name))

    def put_mapping(self, index):
        self.es_client.indices.put_mapping(
            index=index,
            doc_type=self.doc_type,
            body=self.entity.mapping
        )
        self.log("Added mapping for {} in index {}".format(self.doc_type, index))

    def put_alias(self, index):
        self.es_client.indices.put_alias(index=index, name=self.index_alias)
        self.log("Assigned the alias {} to index {}".format(self.index_alias, index))
