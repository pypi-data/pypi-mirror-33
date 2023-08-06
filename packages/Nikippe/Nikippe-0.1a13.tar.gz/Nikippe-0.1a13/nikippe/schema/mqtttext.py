import nikippe.schema.aelement
import nikippe.schema.aelementmqtt


def get_schema():
    schema = nikippe.schema.aelementmqtt.get_schema("mqtttext", "Displays a dynamic text (single line). Every "
                                                                "incoming mqtt message will be displayed.")

    properties = {
        "font": {
            "description": "path to font to be used",
            "type": "string"
        },
        "size": {
            "description": "font size",
            "type": "integer",
            "minimum": 0,
            "exclusiveMinimum": True
        },
        "string": {
            "description": "text to be displayed",
            "type": "string"
        }
    }

    schema = nikippe.schema.aelement.merge(schema, properties)
    return schema
