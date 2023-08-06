import nikippe.schema.statictext
import nikippe.schema.mqtttext
import nikippe.schema.digitalclock
import nikippe.schema.bar
import nikippe.schema.sequentialchart


def get_schema():
    schema = {
                    "description": "List of elements for renderer.",
                    "type": "array",
                    "items": {
                        "oneOf": [
                        ]
                    },
                    "additionalItems": False
            }

    schema["items"]["oneOf"].append(nikippe.schema.statictext.get_schema())
    schema["items"]["oneOf"].append(nikippe.schema.mqtttext.get_schema())
    schema["items"]["oneOf"].append(nikippe.schema.digitalclock.get_schema())
    schema["items"]["oneOf"].append(nikippe.schema.bar.get_schema())
    schema["items"]["oneOf"].append(nikippe.schema.sequentialchart.get_schema())

    return schema
