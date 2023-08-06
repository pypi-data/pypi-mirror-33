#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import jsonschema
from otwstest import compose_schema2version

_version2schema = None


def get_version2schema():
    global _version2schema
    if _version2schema is not None:
        return _version2schema
    current = {
        "$id": "https://tree.opentreeoflife.org/schema/current/tnrs/infer_context.json",
        "type": "object",
        "$schema": "http://json-schema.org/draft-07/schema#",
        "properties": {
            "ambiguous_names": {"type": "array",
                                "items": {"type": "string"}
                                },
            "context_name": {"type": "string"},
            "context_ott_id": {"type": "integer"}
        },
        "required": ["ambiguous_names", "context_name", "context_ott_id"]
    }

    v2 = copy.deepcopy(current)
    _version2schema = compose_schema2version(v2=v2, current=current)
    return _version2schema


def schema_for_version(version):
    return get_version2schema()[version]


def validate(doc, version='current'):
    jsonschema.validate(doc, schema_for_version(version))
    return True
