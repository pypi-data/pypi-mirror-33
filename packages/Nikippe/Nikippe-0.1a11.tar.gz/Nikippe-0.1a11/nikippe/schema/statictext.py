import nikippe.schema.aelement


def get_schema():
    schema = nikippe.schema.aelement.get_schema("statictext", "Displays a static text (single line).")

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
