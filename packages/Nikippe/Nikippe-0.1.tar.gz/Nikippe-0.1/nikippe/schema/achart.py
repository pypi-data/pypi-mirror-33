import nikippe.schema.historyservice
import nikippe.schema.aelement
import nikippe.schema.aelementmqtt


def get_schema(type, description):
    schema = nikippe.schema.aelementmqtt.get_schema(type, description)

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
        "range-minimum": {
            "description": "if set, lower value of chart is limited to this value",
            "type": ["number", "null"]
        },
        "range-maximum": {
            "description": "if set, upper value of chart is limited to this value",
            "type": ["number", "null"]
        },
        "history-service": nikippe.schema.historyservice.get_schema()
    }

    schema = nikippe.schema.aelement.merge(schema, properties)
    schema["required"].remove("range-minimum")
    schema["required"].remove("range-maximum")
    return schema

