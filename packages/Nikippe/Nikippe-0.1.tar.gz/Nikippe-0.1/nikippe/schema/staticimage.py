import nikippe.schema.aelement


def get_schema():
    schema = nikippe.schema.aelement.get_schema("staticimage", "Displays a static image.")

    properties = {
        "image": {
            "description": "path to image to be used",
            "type": "string"
        },
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
