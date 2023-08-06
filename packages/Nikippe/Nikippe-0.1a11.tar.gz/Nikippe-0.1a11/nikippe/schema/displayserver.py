import nikippe.schema.renderer


def get_schema():
    schema = {
        "display-server": {
            "description": "General purpose display server.",
            "type": "object",
            "properties": {
                "topics-pub-image": {
                    "description": "topic to send image to the display driver",
                    "type": "string"
                },
                "send-on-change": {
                    "description": "send new image to epaper if any element reports that it received an update",
                    "type": "boolean"
                },
                "send-interval": {
                    "description": "seconds. if 0 interval is disabled.",
                    "type": "integer",
                    "minimumValue": 0
                },
                "renderer": nikippe.schema.renderer.get_schema()
            },
            "required": ["topics-pub-image", "send-on-change", "send-interval", "renderer"],
            "additionalProperties": False
        }
    }

    return schema


#display-server:
#    topics-pub-image: /test/image  # send image to the display driver
#    send-on-change: True  # send new image to epaper if any element reports that it received an update
#    send-interval: 60  # seconds. if 0 interval is disabled.