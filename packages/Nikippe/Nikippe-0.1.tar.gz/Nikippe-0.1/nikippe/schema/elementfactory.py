import nikippe.schema.mqttimage
import nikippe.schema.statictext
import nikippe.schema.mqtttext
import nikippe.schema.digitalclock
import nikippe.schema.bar
import nikippe.schema.sequentialchart
import nikippe.schema.staticimage
import nikippe.schema.imagelist
import nikippe.schema.circularchart


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
    schema["items"]["oneOf"].append(nikippe.schema.staticimage.get_schema())
    schema["items"]["oneOf"].append(nikippe.schema.mqtttext.get_schema())
    schema["items"]["oneOf"].append(nikippe.schema.digitalclock.get_schema())
    schema["items"]["oneOf"].append(nikippe.schema.bar.get_schema())
    schema["items"]["oneOf"].append(nikippe.schema.sequentialchart.get_schema())
    schema["items"]["oneOf"].append(nikippe.schema.imagelist.get_schema())
    schema["items"]["oneOf"].append(nikippe.schema.mqttimage.get_schema())
    schema["items"]["oneOf"].append(nikippe.schema.circularchart.get_schema())

    return schema
