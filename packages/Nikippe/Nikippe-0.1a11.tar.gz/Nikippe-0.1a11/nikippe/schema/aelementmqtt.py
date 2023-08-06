import nikippe.schema.aelement


def get_schema(element_type, description):
    schema = nikippe.schema.aelement.get_schema(element_type, description)

    schema["properties"]["topic-sub"] = {
        "description": "topic to be subscribed to",
        "type": "string"
    }
    schema["required"].append("topic-sub")

    return schema
