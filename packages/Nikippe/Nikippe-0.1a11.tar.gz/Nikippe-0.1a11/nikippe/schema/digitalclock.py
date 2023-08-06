import nikippe.schema.aelement


def get_schema():
    schema = nikippe.schema.aelement.get_schema("digitalclock", "Displays a digital clock.")

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
    }

    schema = nikippe.schema.aelement.merge(schema, properties)
    return schema
