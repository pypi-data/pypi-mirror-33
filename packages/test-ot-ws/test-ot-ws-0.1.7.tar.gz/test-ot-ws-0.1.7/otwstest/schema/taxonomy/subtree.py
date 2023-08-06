#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import jsonschema
from otwstest import compose_schema2version


def newick_property(version):
    return 'subtree' if version == 'v2' else 'newick'


_version2schema = None


def get_version2schema():
    global _version2schema
    if _version2schema is not None:
        return _version2schema
    current = {
        "$id": "https://tree.opentreeoflife.org/schema/current/taxonomy/subtree.json",
        "type": "object",
        "$schema": "http://json-schema.org/draft-07/schema#",
        "properties": {
        },
    }
    v2 = copy.deepcopy(current)
    n = newick_property('v2')
    v2["properties"][n] = {"type": "string"}
    v2["required"] = [n]
    c = newick_property('current')
    current["properties"][c] = {"type": "string"}
    current["required"] = [c]
    _version2schema = compose_schema2version(v2=v2, current=current)
    return _version2schema


def schema_for_version(version):
    return get_version2schema()[version]


def validate(doc, version='current'):
    jsonschema.validate(doc, schema_for_version(version))
    pname = newick_property(version)
    s = doc[pname]
    if not s.startswith('('):
        c = s if len(s) == 0 else s[0]
        m = 'Expecting "{}" field to be start with a ( found "{}"'.format(pname, c)
        raise jsonschema.ValidationError(m)
    return True
