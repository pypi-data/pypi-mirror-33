def get_schema():
    schema = {
        "description": "Takes incoming data, aggregates it and stores it locally. Optionally, fetches old data from"
                       "dataservice like archippe.",
        "type": "object",
        "properties": {
            "group-by": {
                "description": "time slot duration in seconds. must be > 0",
                "type": "integer",
                "minimum": 0,
                "exclusiveMinimum": True
            },
            "aggregator": {
                "description": "aggregator for group-by. valid values: avg, min, max, median. can be omitted if "
                               "group-by=0.",
                "type": "string",
                "enum": ["avg", "min", "max", "median"]
            },
            "use-dataservice": {
                "description": "use the dataservice archippe to fill the chart with persisted data",
                "type": "boolean"
            },
            "dataservice-request-topic-prefix": {
                "type": "string"
            },
            "dataservice-response-topic-prefix": {
                "type": "string"
            }
        },
        "required": ["group-by", "aggregator"],
        "additionalItems": False
    }

    return schema