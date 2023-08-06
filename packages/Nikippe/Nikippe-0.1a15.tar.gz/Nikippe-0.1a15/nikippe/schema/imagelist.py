import nikippe.schema.aelementmqtt


def get_schema():
    schema = nikippe.schema.aelementmqtt.get_schema("imagelist", "Image list preloads a set of images and displays one "
                                                                 "based on received mqtt-messages.")

    properties = {
        "default-image": {
            "description": "name of image to be displayed before any message has been received",
            "type": "string"
        },
        "images": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "description": "unqiue identifier",
                        "type": "string"
                    },
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
                },
                "required": ["image", "name"],
                "additionalProperties": False
            }
        }
    }

    schema = nikippe.schema.aelement.merge(schema, properties)
    return schema
