#!/usr/bin/env python
# -*- coding: utf-8 -*-

from otwstest.schema.taxonomy.lica import validate


def _mrca_attr(outcome):
    return 'lica' if outcome.api_version == 'v2' else 'mrca'


def _mrca_url_frag(outcome):
    return 'taxonomy/lica' if outcome.api_version == 'v2' else 'taxonomy/mrca'


def _ott_id_attr(outcome):
    return 'ot:ottId' if outcome.api_version == 'v2' else 'ott_id'


def test_bad_taxon(outcome):
    url = outcome.make_url(_mrca_url_frag(outcome))
    expected_bad_id = 55518566
    expected_status = 400
    validator = None
    if outcome.api_version == 'v2':
        expected_status = 200
        validator = validate

    blob = outcome.do_http_json(url, 'POST', data={"ott_ids": [expected_bad_id, 821970, 770319]},
                                validator=validator, expected_status=expected_status)
    if outcome.api_version != 'v2':
        return
    expected_id = 770319
    observered_id = blob['lica'][u'ot:ottId']
    if observered_id != expected_id:
        m = 'Expected LICA ottId to be {} , found {}\n'.format(expected_id, observered_id)
        outcome.exit_test_with_failure(m)
    if u'ott_ids_not_found' not in blob:
        m = "Expected to find list of ott_ids_not_found.\n"
        outcome.exit_test_with_failure(m)
    bad_ids = blob[u'ott_ids_not_found']
    if expected_bad_id not in bad_ids:
        m = 'Expected to find {} in bad ids, found {}\n'.format(expected_bad_id, bad_ids)
        outcome.exit_test_with_failure(m)


test_bad_taxon.api_versions = ('v2', 'v3')


def test_simple(outcome):
    url = outcome.make_url(_mrca_url_frag(outcome))
    outcome.do_http_json(url, 'POST', data={"ott_ids": [515698, 590452, 409712, 643717]},
                         validator=validate)


test_simple.api_versions = ('v2', 'v3')


def test_no_arg(outcome):
    url = outcome.make_url(_mrca_url_frag(outcome))
    expected_status = 400
    if outcome.api_version == 'v2':
        expected_status = 200
        outcome.store('improved_status', 400)
    outcome.do_http_json(url, 'POST', data={"ott_ids": []}, validator=validate,
                         expected_status=expected_status)


test_no_arg.api_versions = ('v2', 'v3')


def test_2(outcome):
    url = outcome.make_url(_mrca_url_frag(outcome))
    blob = outcome.do_http_json(url, 'POST', data={"ott_ids": [901642, 55033]},
                                validator=validate)
    expected_id = 637370
    observered_id = blob[_mrca_attr(outcome)][_ott_id_attr(outcome)]
    if observered_id != expected_id:
        m = 'Expected MRCA ottId to be {} , found {}\n'.format(expected_id, observered_id)
        outcome.exit_test_with_failure(m)


test_2.api_versions = ('v2', 'v3')
