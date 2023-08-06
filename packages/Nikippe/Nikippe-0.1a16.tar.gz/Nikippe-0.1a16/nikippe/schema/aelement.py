def merge(schema, properties):
    for key, value in properties.items():
        schema["properties"][key] = value
        schema["required"].append(key)
    return schema


def get_schema(element_type, description):
    schema = {
            "description": description,
            "type": "object",
            "properties": {
                "name": {
                    "description": "unique name for the element",
                    "type": "string"
                },
                "type": {
                    "description": "type of element",
                    "type": "string",
                    "enum": [element_type]
                },
                "active": {
                    "description": "if set to false, entry will be ignored by entryfactory",
                    "type": "boolean"
                },
                "x": {
                    "description": "x offset",
                    "type": "integer"
                },
                "y": {
                    "description": "y offset",
                    "type": "integer"
                },
                "width": {
                    "description": "width",
                    "type": "integer"
                },
                "height": {
                    "description": "height",
                    "type": "integer"
                },
                "foreground-color": {
                    "description": "foreground-color, 0-255",
                    "type": "integer",
                    "minimumValue": 0,
                    "maximumValue": 255
                },
                "background-color": {
                    "description": "background-color, 0-255",
                    "type": "integer",
                    "minimumValue": 0,
                    "maximumValue": 255
                },
                "transparent-background": {
                    "description": "if set to True the background-color will be transparent.",
                    "type": "boolean"
                }
            },
            "required": ["name", "type", "active", "x", "y", "width", "height", "foreground-color",
                         "background-color"],
            "additionalItems": False
    }

    return schema
