#!/usr/bin/env python
# -*- coding: utf-8 -*-
from otwstest.schema.taxonomy.subtree import validate, newick_property
import re


def test_simple(outcome):
    url = outcome.make_url('taxonomy/subtree')
    result = outcome.do_http_json(url, 'POST', data={"ott_id": 515698}, validator=validate)
    tree = result[newick_property(outcome.api_version)]
    ROOTTAXONSTR = r"\)Barnadesia_ott515698;"
    namecheck = re.compile(ROOTTAXONSTR)
    if re.search(namecheck, tree) is None:
        errstr = 'substring {} does not appear at root of tree:\n {}'
        errstr = errstr.format(ROOTTAXONSTR, tree)
        outcome.exit_test_with_failure(errstr)


test_simple.api_versions = ('v2', 'v3')


def test_des_sp(outcome):
    url = outcome.make_url('taxonomy/subtree')
    result = outcome.do_http_json(url, 'POST', data={"ott_id": 372706}, validator=validate)
    tree = result[newick_property(outcome.api_version)]
    ROOTTAXONSTR = r"\)Canis_ott372706;"
    DESCENDANTTAXONSTR = r"\,Canis_lycaon_ott948004\,"
    namecheck = re.compile(ROOTTAXONSTR)
    namecheck2 = re.compile(DESCENDANTTAXONSTR)
    if re.search(namecheck, tree) is None:
        errstr = 'the expected fragment "{}" does not appear at root of tree'
        outcome.exit_test_with_failure(errstr.format(ROOTTAXONSTR))
    if re.search(namecheck2, tree) is None:
        errstr = 'the expected fragment for terminal taxon "{}" does not appear in tree'
        outcome.exit_test_with_failure(errstr.format(DESCENDANTTAXONSTR))


test_des_sp.api_versions = ('v2', 'v3')
