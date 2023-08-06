#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import jsonschema
from otwstest import compose_schema2version


def get_taxonomy_about_properties(version):
    if version == 'v2':
        return {
            "author": {"type": "string"},
            "name": {"type": "string"},
            "source": {"type": "string"},
            "version": {"type": "string"},
            "weburl": {"type": "string"}
        }
    return {
        "author": {"type": "string"},
        "name": {"type": "string"},
        "source": {"type": "string"},
        "version": {"type": "string"},
        "weburl": {"type": "string"}
    }


_version2schema = None


def get_version2schema():
    global _version2schema
    if _version2schema is not None:
        return _version2schema
    current = {
        "$id": "https://tree.opentreeoflife.org/schema/current/taxonomy/about.json",
        "type": "object",
        "$schema": "http://json-schema.org/draft-07/schema#",
        "properties": get_taxonomy_about_properties('v3'),
        "required": ["author", "name", "source", "version", "weburl"]
    }
    _version2schema = compose_schema2version(v2=copy.deepcopy(current), current=current)
    return get_version2schema()


def schema_for_version(version):
    return get_version2schema()[version]


def validate(doc, version='current'):
    jsonschema.validate(doc, schema_for_version(version))
    if not doc["weburl"].startswith('http'):
        m = 'Expecting "weburl" field to start with http found "{}"'.format(doc['weburl'])
        raise jsonschema.ValidationError(m)
    return True
