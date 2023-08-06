#!/usr/bin/env python
# -*- coding: utf-8 -*-

# !/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from otwstest import is_str_type
import otwstest.schema.tnrs as tnrs
from otwstest.schema.taxonomy.taxon import get_ott_id_property


def test_autocomplete_name(outcome):  # taxonomy-sensitive test
    url = outcome.make_url('tnrs/autocomplete_name')
    search_name = "Endoxyla"
    result = outcome.do_http_json(url, 'POST', data={"name": search_name,
                                                     "context_name": "All life"},
                                  validator=tnrs.autocomplete_name.validate)
    for res in result:
        uname = res["unique_name"]
        if not re.search(search_name, uname):
            errstr = 'unique_name: "{}" of taxon record does not contain search string "{}"'
            outcome.exit_test_with_failure(errstr.format(uname, search_name))


test_autocomplete_name.api_versions = ('v2', 'v3')


def test_contexts(outcome):  # taxonomy-sensitive test
    url = outcome.make_url('tnrs/contexts')
    result = outcome.do_http_json(url, 'POST')
    for top, sub in result.items():
        if not is_str_type(top):
            errstr = 'expecting keys of tnrs/contexts to be strings found {}'
            outcome.exit_test_with_failure(errstr.format(repr(top)))
        if not isinstance(sub, list):
            errstr = 'expecting values of tnrs/contexts to be a list of strings found {}'
            outcome.exit_test_with_failure(errstr.format(repr(sub)))
        for s in sub:
            if not is_str_type(s):
                errstr = 'expecting values of tnrs/contexts to be a list of strings found {}'
                outcome.exit_test_with_failure(errstr.format(repr(s)))
    for k in ('PLANTS', 'ANIMALS', 'FUNGI', 'LIFE', 'MICROBES'):
        if k not in result:
            errstr = 'Missing key in context listing: "{}"'.format(k)
            outcome.exit_test_with_failure(errstr)
    if 'Archaea' not in result['MICROBES']:
        errstr = 'Archaea not in context MICROBES'
        outcome.exit_test_with_failure(errstr)
    if 'Arachnids' not in result['ANIMALS']:
        errstr = 'Arachnides not in context ANIMALS.'
        outcome.exit_test_with_failure(errstr)


test_contexts.api_versions = ('v2', 'v3')


def test_infer_context(outcome):  # taxonomy-sensitive test
    url = outcome.make_url('tnrs/infer_context')
    data = {"names": ["Pan", "Homo", "Mus musculus", "Upupa epops"]}
    result = outcome.do_http_json(url, 'POST', data=data,
                                  validator=tnrs.infer_context.validate)
    if result['context_name'] != 'Tetrapods':
        errstr = 'Expected context_name = Tetrapods, found "{}"'.format(result['context_name'])
        outcome.exit_test_with_failure(errstr)
    if result['ambiguous_names']:
        errstr = 'Expected no ambiguous_names, but found {}.'.format(result['ambiguous_names'])
        outcome.exit_test_with_failure(errstr)


test_infer_context.api_versions = ('v2', 'v3')


def test_match_names(outcome):  # taxonomy-sensitive test
    url = outcome.make_url('tnrs/match_names')
    test_list = ["Aster", "Symphyotrichum", "Erigeron", "Barnadesia", "Hylobates"]
    test_ids = [409712, 1058735, 643717, 515698, 166552]
    data = {"names": test_list}
    result = outcome.do_http_json(url, 'POST', data=data,
                                  validator=tnrs.match_names.validate)
    mni = result[tnrs.match_names.matched_name_list_prop(outcome.api_version)]
    if set(test_list) != set(mni):
        errstr = "Failed to match, submitted: {}, returned {}"
        outcome.exit_test_with_failure(errstr.format(test_list, mni))
    match_list = result['results']
    ott_id_prop = get_ott_id_property(outcome.api_version)
    for match in match_list:
        m = match['matches'][0]
        t = m if outcome.api_version == 'v2' else m['taxon']
        if t.get(ott_id_prop) not in test_ids:
            errstr = "bad match return {}, expected one of {}"
            outcome.exit_test_with_failure(errstr.format(m.get(u'ot:ottId'), test_ids))
        if m.get(u'matched_name') not in test_list:
            errstr = "bad match return {}, expected one of {}"
            outcome.exit_test_with_failure(errstr.format(m.get(u'matched_name'), test_list))


test_match_names.api_versions = ('v2', 'v3')


def test_match_hyphenated(outcome):  # taxonomy-sensitive test
    url = outcome.make_url('tnrs/match_names')
    test_list = ["Polygonia c-album"]
    test_ids = [522165]
    data = {"names": test_list}
    result = outcome.do_http_json(url, 'POST', data=data,
                                  validator=tnrs.match_names.validate)
    mni = result[tnrs.match_names.matched_name_list_prop(outcome.api_version)]
    if set(test_list) != set(mni):
        errstr = "Failed to match, submitted: {}, returned {}"
        outcome.exit_test_with_failure(errstr.format(test_list, mni))
    match_list = result['results']
    ott_id_prop = get_ott_id_property(outcome.api_version)
    for match in match_list:
        m = match['matches'][0]
        t = m if outcome.api_version == 'v2' else m['taxon']
        if t.get(ott_id_prop) not in test_ids:
            errstr = "bad match return {}, expected one of {}"
            outcome.exit_test_with_failure(errstr.format(m.get(u'ot:ottId'), test_ids))


test_match_hyphenated.api_versions = ('v2', 'v3')
