# Aasaanjobs Elasticsearch SDK
Library to handle elasticsearch related transactions in Python (for internal usage in Aasaanjobs)

## Requirements

- Python 3.5 and greater
- Elasticsearch Python

## Installation

Install using `pip`
```
pip install ajelastic
```

## Configuration

The AJ Elastic library reads configurations from module path specified in the environment
variable `AJELASTIC_SETTINGS_MODULE` if its a standalone python project, or the 
`DJANGO_SETTINGS_MODULE` environment variable if its a Django project.
```
export AJELASTIC_SETTINGS_MODULE=tests.settings
```

#### Example

Below is an example settings module that can be consumed by the library
```python
# Mandatory Settings

# Elasticsearch host and port
ES_HOST = "http://localhost:9200"
# The environment suffix that will be added in the Elasticsearch index names
ES_ENV = "development"              

# Optional Settings

# List of Elasticsearch indices
ES_INDICES = {
    "User": {
        "name": "users",                                # The index name prefix
        "doc_type": "user",                             # Elastic document type
        "data_functions": {                             
            "single": "tests.data:get_user",          # Function to fetch a user; should accept a single ID argument
            "multi": "tests.data:list_users"          # Function to fetch list of users; should accept two arguments; limit and offset
        },
        "mapping_path": "tests/user_mapping.json"    # Path to the JSON mapping of the document structure
    }
}
```

## Commands to Sync Data with Elasticsearch

This library provides the following command line scripts to synchronize/initialize data

#### `aj-es-reindex`
This command will reindex the documents from scratch fetching data from the function defined in the `data_functions.multi`
settings of the entity (i.e., withing the `ES_INDICES` settings).

For eg, the below command will reindex the User entity, fetching data from the `list_users` function (as specified in the settings)
with a batch size of 100, i.e., in a single request 100 users will be index to elasticsearch.
```
aj-es-reindex User 100
```
