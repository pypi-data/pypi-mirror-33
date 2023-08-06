import nikippe.schema.elementfactory


def get_schema():
    schema = {
        "description": "Renderer controls the single elements and generates an updated image whenever requested.",
        "type": "object",
        "properties": {
            "width": {
                "description": "image width",
                "type": "integer",
                "minimum": 0,
                "exclusiveMinimum": True
            },
            "height": {
                "description": "image height",
                "type": "integer",
                "minimum": 0,
                "exclusiveMinimum": True
            },
            "background": {
                "description": "path to background image",
                "type": "string"
            },
            "background-color": {
                "description": "background color for base image. valid values: 0 - 255",
                "type": "integer",
                "minimumValue": 0,
                "maximumValue": 255
            },
            "elements": {
            }
        },
        "required": ["width", "height", "background-color", "elements"],
        "additionalProperties": False
    }

    schema["properties"]["elements"] = nikippe.schema.elementfactory.get_schema()

    return schema


#width: 250
#height: 122
#background:../ resources / gui_background_2.13.png  # optional
#background - color: 255  # either 0 or 255.
#elements: