import nikippe.schema.aelement
import nikippe.schema.aelementmqtt


def get_schema():
    schema = nikippe.schema.aelementmqtt.get_schema("sequentialchart", "Regular chart with the latest values added at the right "
                                                            "and the oldest values on the left.")

    properties = {
        "border-top": {
            "type": "boolean"
        },
        "border-bottom": {
            "type": "boolean"
        },
        "border-left": {
            "type": "boolean"
        },
        "border-right": {
            "type": "boolean"
        },
        "group-by": {
            "description": "time slot duration in seconds. no grouping = 0",
            "type": "integer",
            "minimum": 0
        },
        "connect-values": {
            "description": "aggregator for group-by. valid values: avg, min, max, median. can be omitted if group-by=0.",
            "type": "boolean"
        },
        "pixel-per-value": {
            "description": "a new value/dot is drawn every n-th pixel on the x-axis. must be > 0.",
            "type": "integer",
            "minimum": 0,
            "exclusiveMinimum": True
        },
        "aggregator": {
            "description": "aggregator for group-by. valid values: avg, min, max, median. can be omitted if "
                           "group-by=0.",
            "type": "string",
            "enum": ["avg", "min", "max", "median"]
        }
    }

    schema = nikippe.schema.aelement.merge(schema, properties)
    schema["required"].remove("aggregator")
    return schema

