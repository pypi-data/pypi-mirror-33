#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import jsonschema
from otwstest import compose_schema2version


def get_ott_id_property(version):
    return "ot:ottId" if version == 'v2' else 'ott_id'


def get_ott_name_property(version):
    return "ot:ottTaxonName" if version == 'v2' else 'name'


def taxon_obj_properties(version):
    p = {
        "flags": {
            "type": "array",
            "items": {"type": "string"}
        },
        "rank": {"type": "string"},
        "synonyms": {
            "type": "array",
            "items": {"type": "string"}
        },
        "tax_sources": {
            "type": "array",
            "items": {"type": "string"}
        },
        "unique_name": {"type": "string"},
        get_ott_id_property(version): {"type": "integer"},
        get_ott_name_property(version): {"type": "string"}
    }
    if version == 'v2':
        p["node_id"] = {"type": "integer"}
    else:
        p["is_suppressed"] = {"type": "boolean"}
    return p


_version2schema = None


def get_version2schema():
    global _version2schema
    if _version2schema is not None:
        return _version2schema
    current = {
        "$id": "https://tree.opentreeoflife.org/schema/current/taxonomy/taxon.json",
        "type": "object",
        "definitions": {},
        "$schema": "http://json-schema.org/draft-07/schema#"
    }
    v2 = copy.deepcopy(current)
    v2['properties'] = taxon_obj_properties('v2')
    current['properties'] = taxon_obj_properties('v3')
    _version2schema = compose_schema2version(v2=v2, current=current)
    return _version2schema


def schema_for_version(version):
    return get_version2schema()[version]


def validate(doc, version='current'):
    jsonschema.validate(doc, schema_for_version(version))
    return True
