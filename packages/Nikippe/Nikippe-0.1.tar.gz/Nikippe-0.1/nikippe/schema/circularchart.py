import nikippe.schema.achart


def get_schema():
    schema = nikippe.schema.achart.get_schema("circularchart", "A circular chart with a static time axis.")

    properties = {
        "draw-cursor": {
            "description": "draw a cursor at the current time slot",
            "type": "boolean"
        },
        "time-span": {
            "description": "Week, Day, Hour, Minute",
            "type": "string",
            "enum": ["Week", "WEEK", "week", "Day", "DAY", "day", "Hour", "HOUR", "hour", "Minute", "MINUTE", "minute"]
        }
    }

    schema = nikippe.schema.aelement.merge(schema, properties)

    return schema

