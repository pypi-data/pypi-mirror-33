import json
import traceback

from elasticsearch import NotFoundError

from .base import BaseElasticCommand


class ReindexCommand(BaseElasticCommand):
    name = "ElasticReindex"
    description = """Reindex the entity from scratch by fetching data
    from multi data function specified in the entity
    settings (ES_INDICES)"""

    def index(self, new_index, batch_size):
        limit, offset = batch_size, 0
        stop = False
        while not stop:
            bulk_data = []
            data = self.entity.data_fns.multi(limit, offset)
            for _ in data:
                bulk_data.append(json.dumps({
                    "index": {
                        "_index": new_index,
                        "_type": self.doc_type,
                        "_id": _["id"]
                    }
                }))
                bulk_data.append(json.dumps(_))
            if not bulk_data:
                break
            self.es_client.bulk(body="\n".join(bulk_data))
            self.log(
                "Indexed {} documents (Iteration no. {})"
                .format(
                    int(len(bulk_data)/2),
                    int(offset/limit) + 1
                )
            )
            offset += limit
    
    def run(self):
        # Try to find the older index for the entity
        try:
            old_index = self.get_old_index()
        except NotFoundError:
            self.log_err("No old index found")
            old_index = None
        # Create a new index for the entity
        new_index = self.create_index()
        try:
            self.put_mapping(new_index)
            self.index(new_index, self.batch_size)
            self.put_alias(new_index)
            # Delete the older index if exists
            if old_index:
                self.delete_index(old_index)
        except Exception as ex:
            self.log_err("Failed to index, reason: {}".format(ex))
            traceback.print_exc()
            # Delete the new index created
            self.delete_index(new_index)


def main():
    cmd = ReindexCommand()
    cmd.run()
