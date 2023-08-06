#!/usr/bin/env python
# -*- coding: utf-8 -*-

from otwstest.schema.taxonomy.flags import validate


def test_simple(outcome):
    url = outcome.make_url('taxonomy/flags')
    outcome.do_http_json(url, 'POST', validator=validate)


test_simple.api_versions = ('v2', 'v3')
