#!/usr/bin/env python
# -*- coding: utf-8 -*-
from otwstest.schema.taxonomy.taxon import validate, get_ott_id_property, get_ott_name_property
from otwstest import demand_property


def taxon_url_frag(outcome):
    return 'taxonomy/taxon' if outcome.api_version == 'v2' else 'taxonomy/taxon_info'


def term_des_arg(outcome):
    return '{}_terminal_descendants'.format('list' if outcome.api_version == 'v2' else 'include')


def lineage_prop(outcome):
    return 'taxonomic_lineage' if outcome.api_version == 'v2' else 'lineage'


def test_simple(outcome):  # taxonomy-sensitive test
    url = outcome.make_url(taxon_url_frag(outcome))
    result = outcome.do_http_json(url, 'POST', data={"ott_id": 901642}, validator=validate)
    expected = u'Alseuosmia banksii'
    prop = get_ott_name_property(outcome.api_version)
    obs = result[prop]
    if obs != expected:
        errstr = 'Expected taxon name "{}", but found in "{}"'.format(expected, obs)
        outcome.exit_test_with_failure(errstr)


test_simple.api_versions = ('v2', 'v3')


def _check_ott_id(result, outcome, ott_id):
    prop = get_ott_id_property(outcome.api_version)
    if result[prop] != ott_id:
        errstr = 'Incorrect ott_id in returned taxon {}', format(result[prop])
        outcome.exit_test_with_failure(errstr)


def test_include_children(outcome):  # taxonomy-sensitive test
    url = outcome.make_url(taxon_url_frag(outcome))
    result = outcome.do_http_json(url, 'POST', data={"ott_id": 515698, "include_children": "true"},
                                  validator=validate)
    _check_ott_id(result, outcome, 515698, )
    demand_property(u'children', result, outcome, 'taxon')
    expected_child = 503056
    prop = get_ott_id_property(outcome.api_version)
    if expected_child not in map(lambda c: c[prop], result[u'children']):
        errstr = 'Expected child {} not found in result'.format(expected_child)
        outcome.exit_test_with_failure(errstr)


test_include_children.api_versions = ('v2', 'v3')


def test_include_lineage(outcome):
    url = outcome.make_url(taxon_url_frag(outcome))
    result = outcome.do_http_json(url, 'POST', data={"ott_id": 515698, "include_lineage": "true"},
                                  validator=validate)
    _check_ott_id(result, outcome, 515698)
    demand_property(lineage_prop(outcome), result, outcome, 'taxon')


test_include_lineage.api_versions = ('v2', 'v3')


def test_tax_sources(outcome):  # taxonomy-sensitive test
    url = outcome.make_url(taxon_url_frag(outcome))
    result = outcome.do_http_json(url, 'POST', data={"ott_id": 766177}, validator=validate)
    sources = demand_property('tax_sources', result, outcome, 'taxon')
    for e in ['ncbi:58228', 'gbif:3189571', 'irmng:11346207']:
        if e not in sources:
            errstr = 'Expected "{}" not found in tax_sources'.format(e)
            outcome.exit_test_with_failure(errstr)


test_tax_sources.api_versions = ('v2', 'v3')


def test_terminal(outcome):  # taxonomy-sensitive test
    url = outcome.make_url(taxon_url_frag(outcome))
    result = outcome.do_http_json(url, 'POST', data={"ott_id": 1066581,
                                                     term_des_arg(outcome): True},
                                  validator=validate)
    descendants = demand_property('terminal_descendants', result, outcome, 'taxon')
    if not {490099, 1066590}.issubset(set(descendants)):
        errstr = "Bos taurus (490099) and Bos primigenius (1066590) not returned as " \
                 "descendants of Bos (1066581)\n"
        outcome.exit_test_with_failure(errstr)


test_terminal.api_versions = ('v2', 'v3')
