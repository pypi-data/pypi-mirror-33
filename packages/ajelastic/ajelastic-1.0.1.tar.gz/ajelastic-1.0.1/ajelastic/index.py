import json

from elasticsearch import Elasticsearch

from .definition import ElasticIndex
from .conf import settings


class BaseService:
    def __init__(self, entity: ElasticIndex):
        assert isinstance(entity, ElasticIndex), "Invalid entity provided, should be an object of ElasticIndex"
        self.entity = entity
        self.client = Elasticsearch(settings.ES_HOST)

    @property
    def index(self):
        return self.entity.index

    @property
    def doc_type(self):
        return self.entity.doc_type


class Index(BaseService):
    def __init__(self, *args, **kwargs):
        self.validate(**kwargs)
        super().__init__(*args, **kwargs)
        self.entity_id = self.get_entity_id(**kwargs)
        partial = kwargs.get("partial", False)
        is_script = kwargs.get("is_script", False)
        self.do_update = False
        if partial:
            self.body = dict(doc=kwargs["data"])
            self.do_update = True
        elif is_script:
            self.body = dict(script=kwargs["data"])
            self.do_update = True
        elif kwargs.get("data"):
            self.body = kwargs.pop("data")
        else:
            self.body = self.entity.data_fns.single(self.entity_id)

    @staticmethod
    def validate(**kwargs):
        if kwargs.get("partial") and not kwargs.get("data"):
            raise AssertionError("Missing/None argument \'data\' on partial index job.")
        if kwargs.get("is_script") and not kwargs.get("data"):
            raise AssertionError("Missing/None argument \'data\' on script index job.")
        if kwargs.get("partial") and kwargs.get("is_script"):
            raise AssertionError("Don't provide both is_script and partial as True.")
        if not kwargs.get("id") and not kwargs.get("data"):
            raise AssertionError("Missing/None argument \'id\' received.")

    @staticmethod
    def get_entity_id(**kwargs):
        if kwargs.get("id"):
            return kwargs.pop("id")
        elif kwargs.get("data") and kwargs["data"].get("id"):
            return kwargs["data"]["id"]
        else:
            raise AssertionError("Missing/None argument \'id\'.")

    def __call__(self):
        kwargs = {
            "index": self.index,
            "doc_type": self.doc_type,
            "id": self.entity_id,
            "body": self.body
        }
        if self.do_update:
            self.client.update(**kwargs)
        else:
            self.client.index(**kwargs)


class BulkUpdate(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert kwargs.get("data"), "Missing/None argument \'data\'."
        self.data = kwargs.pop("data")
        self.entity_ids = kwargs.pop("entity_ids", [])
        assert len(self.entity_ids), "Empty list received from argument \'entity_ids\'."

    def __call__(self):
        bulk_body = []
        for entity_id in self.entity_ids:
            bulk_body.append(json.dumps({
                "update": {
                    "_index": self.index,
                    "_type": self.doc_type,
                    "_id": str(entity_id)
                }
            }))
            bulk_body.append(json.dumps({"doc": self.data}))
        self.client.bulk(body="\n".join(bulk_body))
