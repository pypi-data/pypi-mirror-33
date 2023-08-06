import nikippe.schema.aelement
import nikippe.schema.aelementmqtt


def get_schema():
    schema = nikippe.schema.aelementmqtt.get_schema("bar", "Bar element - displays the current value relative to the "
                                                "configured minimum and maximum values.")

    properties = {
        "orientation": {
            "description": "up, down, left, right",
            "type": "string",
            "enum": ["up", "Up", "UP", "down", "Down", "DOWN", "left", "Left", "LEFT", "right", "Right", "RIGHT"]
        },
        "border": {
            "description": "If true, draw a 1 pixel border on all sides with foreground color.",
            "type": "boolean"
        },
        "min-value": {
            "description": "minimum value to be displayed",
            "type": "number"
        },
        "max-value": {
            "description": "maximum value to be displayed",
            "type": "number"
        }
    }

    schema = nikippe.schema.aelement.merge(schema, properties)
    return schema
