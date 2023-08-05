def get_schema():
    schema = {
        "data-persistence": {
            "description": "Archippe is a data persistence micro service for pelops.",
            "type": "object",
            "properties": {
                "topics": {
                    "description": "list of topics that should be persisted",
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string"
                            },
                            "type": {
                                "description": "convert message to this value",
                                "type": "string",
                                "enum": ["boolean", "BOOLEAN", "Boolean",
                                         "string", "String", "STRING",
                                         "float", "Float", "FLOAT",
                                         "integer", "Integer", "INTEGER"
                                         ]
                            }
                        },
                        "required": ["topic", "type"],
                        "additionalProperties": False
                    }
                },
                "topic-request-prefix": {
                    "description": "prefix for each topic to request historic data",
                    "type": "string"
                },
                "topic-response-prefix": {
                    "description": "prefix for each topic to publish historic data",
                    "type": "string"
                }
            },
            "required": ["topics", "topic-request-prefix", "topic-response-prefix"],
            "additionalProperties": False
        }
    }
    return schema

