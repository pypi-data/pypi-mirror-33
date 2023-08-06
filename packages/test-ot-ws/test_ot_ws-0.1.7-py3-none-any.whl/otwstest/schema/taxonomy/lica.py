#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import jsonschema
from .taxon import taxon_obj_properties
from otwstest import compose_schema2version

_version2schema = None


def get_version2schema():
    global _version2schema
    if _version2schema is not None:
        return _version2schema

    current = {
        "$id": "https://tree.opentreeoflife.org/schema/current/taxonomy/mrca.json",
        "type": "object",
        "definitions": {},
        "$schema": "http://json-schema.org/draft-07/schema#",
        "properties": {
            "mrca": {
                "type": "object"
            },
            "ott_ids_not_found": {
                "type": "array",
                "items": {"type": "integer"}
            }
        }
    }
    v2 = copy.deepcopy(current)
    v2['properties']['mrca']['properties'] = taxon_obj_properties('v2')
    current['properties']['mrca']['properties'] = taxon_obj_properties('v3')
    _version2schema = compose_schema2version(v2=v2, current=current)
    return _version2schema


def schema_for_version(version):
    return get_version2schema()[version]


def validate(doc, version='current'):
    jsonschema.validate(doc, schema_for_version(version))
    return True
