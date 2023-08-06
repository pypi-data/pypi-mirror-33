#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import jsonschema
from otwstest import compose_schema2version

_version2schema = None


def suppressed_property(version):
    return "is_dubious" if version == 'v2' else 'is_suppressed'


def get_version2schema():
    global _version2schema
    if _version2schema is not None:
        return _version2schema
    current = {
        "$id": "https://tree.opentreeoflife.org/schema/current/tnrs/autocomplete_name.json",
        "type": "array",
        "$schema": "http://json-schema.org/draft-07/schema#",
        "items": {
            "type": "object"
        }
    }
    v2 = copy.deepcopy(current)
    add_taxon_properties(current["items"], 'current')
    add_taxon_properties(v2["items"], 'v2')
    _version2schema = compose_schema2version(v2=v2, current=current)
    return _version2schema


def add_taxon_properties(par, version):
    p = {
        suppressed_property(version): {"type": "boolean"},
        "is_higher": {"type": "boolean"},
        "unique_name": {"type": "string"},
    }
    if version == 'v2':
        p["node_id"] = {"type": "integer"}
        p["ot:ottId"] = {"type": "integer"}
    else:
        p["ott_id"] = {"type": "integer"}
    par["properties"] = p
    par["required"] = list(p.keys())
    par["required"].sort()


def schema_for_version(version):
    return get_version2schema()[version]


def validate(doc, version='current'):
    jsonschema.validate(doc, schema_for_version(version))
    return True
