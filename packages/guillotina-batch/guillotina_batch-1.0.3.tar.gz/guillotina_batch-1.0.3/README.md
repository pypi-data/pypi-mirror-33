# Guillotina Batch Docs

This package simple provides a `@batch` endpoint to Guillotina which
allows you to group multiple requests into one.


## Configuration

Just add a few lines to your config.yml::

  {"applications": ["guillotina_batch"]}


## Usage

The `@batch` endpoint takes a array of batch definitions taking the following parameters:

- method:str
- endpoint:str
- headers:object[str, str]
- payload:object


For example::

```
POST /db/container/@batch [{
    "method": "POST",
    "endpoint": "path/to/object/@sharing",
    "payload": {
        "prinperm": [{
            "principal": "user1",
            "permission": "guillotina.AccessContent",
            "setting": "AllowSingle"
        }]
    }
},{
    "method": "POST",
    "endpoint": "path/to/object2/@sharing",
    "payload": {
        "prinperm": [{
            "principal": "user1",
            "permission": "guillotina.AccessContent",
            "setting": "AllowSingle"
        }]
    }
}]

```