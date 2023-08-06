import nikippe.schema.aelementmqtt


def get_schema():
    schema = nikippe.schema.aelementmqtt.get_schema("mqttimage", "Displays images that are received via mqtt messages.")

    properties = {
        "offset_x": {
            "description": "offset for image within element plane (optional, default=0)",
            "type": "integer"
        },
        "offset_y": {
            "description": "offset for image within element plane (optional, default=0)",
            "type": "integer"
        }
    }

    schema = nikippe.schema.aelement.merge(schema, properties)
    schema["required"].remove("offset_x")
    schema["required"].remove("offset_y")
    return schema
