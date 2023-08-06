#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import sys
import types
import traceback
import codecs
import json
import threading
import re
import copy

__version__ = '0.1.7'
try:
    from enum import Enum
    # noinspection PyCompatibility
    from queue import Queue
except ImportError:
    # noinspection PyPackageRequirements,PyUnresolvedReferences
    from enum import Enum
    # noinspection PyCompatibility,PyUnresolvedReferences
    from Queue import Queue
import requests
import jsonschema

if sys.version_info.major == 2:
    # noinspection PyUnresolvedReferences
    def is_str_type(x):
        # noinspection PyCompatibility
        return isinstance(x, basestring)
else:
    def is_str_type(x):
        return isinstance(x, str)

TEST_QUEUE = Queue()
ALL_PASSED = True
ALL_PASSED_LOCK = threading.Lock()


def compose_schema2version(v2, current):
    v3 = copy.deepcopy(current)
    v3['$id'] = v3['$id'].replace('/current/', '/v3/')
    v2['$id'] = v2['$id'].replace('/current/', '/v3/')
    return {'current': current, 'v2': v2, 'v3': v3}


def _run_queued_test():
    global ALL_PASSED
    while True:
        try:
            blob = TEST_QUEUE.get_nowait()
        except Exception:
            break
        fn, outcome, test_config = blob
        ok = test_config.run_spawned_test(outcome, fn)
        if not ok:
            with ALL_PASSED_LOCK:
                ALL_PASSED = False


def run_tests(test_config, addr_fn_pairs_list, test_results):
    for test_addr, fn in addr_fn_pairs_list:
        outcome = test_results.spawning_test(test_config, test_addr)
        TEST_QUEUE.put((fn, outcome, test_config))

    threads = []
    for i in range(min(test_config.num_threads, TEST_QUEUE.qsize())):
        threads.append(threading.Thread(target=_run_queued_test))
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    with ALL_PASSED_LOCK:
        return ALL_PASSED


def write_as_json(blob, dest, indent=0, sort_keys=True):
    """Writes `blob` as JSON to the filepath `dest` or the filestream `dest` (if it isn't a string)
    uses utf-8 encoding if the filepath is given (does not change the encoding if dest is already open).
    """
    opened_out = False
    if is_str_type(dest):
        out = codecs.open(dest, mode='w', encoding='utf-8')
        opened_out = True
    else:
        out = dest
    try:
        if indent == 0:
            json.dump(blob, out, indent=indent, sort_keys=sort_keys)
        else:
            json.dump(blob, out, indent=indent, sort_keys=sort_keys, separators=(',', ': '))
        out.write('\n')
    finally:
        out.flush()
        if opened_out:
            out.close()


class TestEarlyExit(Exception):
    pass


class TestStatus(Enum):
    """Status integer used by TestOutcome instances"""
    RUNNING = 0
    SUCCESS = 1
    FAILED = 2
    ERROR = 3
    SKIPPED = 4
    UNCAUGHT_EXCEPTION = 5  # error not caught by test function


STATUS_REPORT_ORDER = ['SUCCESS', 'SKIPPED',  # not problematic
                       'NOT_RECORDED', 'UNKNOWN',  # report ignorance states, not real statuses
                       'RUNNING', 'FAILED', 'ERROR', 'UNCAUGHT_EXCEPTION',  # problematic
                       ]
STATUS_TO_SINGLE_LTR = {TestStatus.SUCCESS: '.',
                        TestStatus.ERROR: 'E',
                        TestStatus.FAILED: 'f',
                        TestStatus.SKIPPED: 's',
                        TestStatus.UNCAUGHT_EXCEPTION: 'X',
                        }


class TestResults(object):
    _lock = threading.RLock()

    def __init__(self):
        with TestResults._lock:
            self._run = []
            self._succeeded = []
            self._errored = []
            self._failed = []
            self._skipped = []
            self._exceptions_uncaught = []
            self._spawned_unfinished = set()
            self._status2list = {TestStatus.SUCCESS: self._succeeded,
                                 TestStatus.ERROR: self._errored,
                                 TestStatus.FAILED: self._failed,
                                 TestStatus.SKIPPED: self._skipped,
                                 TestStatus.UNCAUGHT_EXCEPTION: self._exceptions_uncaught,
                                 }

    def flush(self, context):
        if context.noise_level >= 1 and len(self._run) > 0:
            m = '\n{} test(s) run. {} succeeded. {} skipped. {} failed. {} errored. ' \
                '{} raised exceptions.   {}/{} success rate.'
            with TestResults._lock:
                m = m.format(len(self._run), len(self._succeeded), len(self._skipped),
                             len(self._failed), len(self._errored), len(self._exceptions_uncaught),
                             len(self._succeeded), len(self._run) - len(self._skipped))
            context.status_message(1, m)

    def _reg_as_finished(self, outcome):
        with TestResults._lock:
            self._run.append(outcome)
            try:
                self._spawned_unfinished.remove(outcome)
            except Exception:
                pass

    def register(self, outcome):
        with TestResults._lock:
            self._reg_as_finished(outcome)
            self._status2list[outcome.status].append(outcome)

    @property
    def num_problems(self):
        with TestResults._lock:
            return sum([len(i) for i in (self._failed, self._errored, self._exceptions_uncaught)])

    # noinspection PyUnusedLocal
    def spawning_test(self, config, test_addr):
        tout = TestOutcome(self, test_addr, config)
        with TestResults._lock:
            self._spawned_unfinished.add(tout)
        return tout


_VERS_SPEC_PAT = re.compile(r'^v[0-9.]+$')


class TestOutcome(object):
    def __init__(self, results_obj, test_addr, config):
        self.test_addr = test_addr
        self.config = config
        self.status = TestStatus.RUNNING
        self._results_collection = results_obj
        self._data = {}
        poss_v = test_addr.split('.')[-1]
        assert (_VERS_SPEC_PAT.match(poss_v))
        self.api_version = poss_v

    def store(self, key, value):
        self._data[key] = value

    def get(self, key, default):
        return self._data.setdefault(key, default)

    @property
    def succeeded(self):
        return self.status == TestStatus.SUCCESS

    def __hash__(self):
        return hash(self.test_addr)

    def make_url(self, frag):
        while frag.startswith('/'):
            frag = frag[1:]
        return self.config.configure_url('{}/{}'.format(self.api_version, frag))

    def uncaught(self, ex_message):
        self.status = TestStatus.UNCAUGHT_EXCEPTION
        self.store('exception', ex_message)

    def _finalize(self):
        if self.status == TestStatus.RUNNING:
            self.status = TestStatus.SUCCESS

    def record(self, config):
        self._finalize()
        if self._results_collection:
            self._results_collection.register(self)
        self.serialize(config)
        config.status_message(2, STATUS_TO_SINGLE_LTR[self.status])
        if self.status != TestStatus.SUCCESS and config.noise_level > 2:
            if config.noise_level == 3:
                self.brief_diagnosis(config)
            else:
                self.full_diagnosis(config)

    def brief_diagnosis(self, config):
        m = None
        if self.status == TestStatus.UNCAUGHT_EXCEPTION:
            m = 'Exception not handled by test function (please report this error)'
        elif self.status != TestStatus.SUCCESS:
            m = '{}. {}'.format(_tstatus_to_str(self.status), self.get('brief', ''))
        if m:
            config.status_message(3, '{}: {}\n'.format(clean_test_addr(self.test_addr), m))

    def full_diagnosis(self, config):
        m = None
        if self.status == TestStatus.UNCAUGHT_EXCEPTION:
            m = 'Exception not handled by test function (please report this error).\nException:\n'
            m += self._data['exception']
        elif self.status != TestStatus.SUCCESS:
            m = '{}. {}'.format(_tstatus_to_str(self.status), self.get('detailed', ''))
        if m:
            config.status_message(4, '{}: {}\n'.format(clean_test_addr(self.test_addr), m))

    def serialize(self, config):
        results_dir = config.get_results_dir(self.test_addr)
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
        outf = os.path.join(results_dir, '{}_outcome.json'.format(self.api_version))
        self.store('status', _tstatus_to_str(self.status))
        self.store('test_addr', self.test_addr)
        write_as_json(self._data, outf, indent=2)

    # noinspection PyMethodMayBeStatic
    def raise_for_status(self, resp):
        try:
            resp.raise_for_status()
        except Exception as e:
            try:
                j = resp.json()
                m = '\n    '.join(['"{k}": {v}'.format(k=k, v=v) for k, v in j.items()])
                sys.stderr.write('resp.json = {t}'.format(t=m))
            except Exception:
                if resp.text:
                    sys.stderr.write('resp.text = {t}\n'.format(t=resp.text))
            raise e

    # noinspection PyShadowingNames
    def do_http_json(self,
                     url,
                     verb='GET',
                     data=None,
                     headers=None,
                     expected_status=200,
                     expected_response=None,
                     schema=None,
                     validator=None):
        """Call `url` with the http method of `verb`.
        If specified `data` is passed using json.dumps
        returns True if the response:
             has the expected status code, AND
             has the expected content (if expected_response is not None)
        """
        if not self.config.testing_api_version(self.api_version):
            self.exit_test_with_skipped('api {} tests skipped'.format(self.api_version))
        if headers is None:
            headers = {'content-type': 'application/json', 'accept': 'application/json', }
        resp, call_out = self.request(verb, url, headers, data=data)
        call_out['expected_status_code'] = expected_status
        if resp.status_code != expected_status:
            m = 'Wrong status code. Expected {}. Got {}.'.format(resp.status_code, expected_status)
            self.exit_test_with_error(m)
        results = resp.json()
        call_out['response_body'] = results
        if schema is not None or validator is not None:
            try:
                if schema is not None:
                    jsonschema.validate(results, schema)
                if validator is not None:
                    validator(results, self.api_version)
            except jsonschema.ValidationError as x:
                m = 'Invalid response body. Validator says: {}'.format(str(x))
                self.exit_test_with_error(m)
        if expected_response is not None:
            if results != expected_response:
                call_out['expected_response_body'] = expected_response
                m = 'Wrong response body. Expected {}. Got {}.'.format(results, expected_response)
                self.exit_test_with_error(m)
        return results

    def request(self, verb, url, headers, data=None):
        call_out = self.get('calls', [])
        stored = {'url': url, 'verb': verb, 'headers': headers, 'data': data}
        call_out.append(stored)
        if data:
            resp = requests.request(verb,
                                    url,
                                    headers=headers,
                                    data=json.dumps(data),
                                    allow_redirects=True)
        else:
            resp = requests.request(verb,
                                    url,
                                    headers=headers,
                                    allow_redirects=True)
        stored['status_code'] = resp.status_code
        debug('Sent {v} to {s}'.format(v=verb, s=resp.url))
        return resp, stored

    def exit_test_with_error(self, brief, detailed=None):
        self.status = TestStatus.ERROR
        self._set_explanation(brief, detailed)
        raise TestEarlyExit()

    def exit_test_with_failure(self, brief, detailed=None):
        self.status = TestStatus.FAILED
        self._set_explanation(brief, detailed)
        raise TestEarlyExit()

    def exit_test_with_skipped(self, brief, detailed=None):
        self.status = TestStatus.SKIPPED
        self._set_explanation(brief, detailed)
        raise TestEarlyExit()

    def _set_explanation(self, brief, detailed):
        self.store('brief', brief)
        self.store('detailed', detailed if detailed else brief)


def _tstatus_to_str(status):
    return str(status)[len('TestStatus.'):]


SYST_CHOICES = frozenset(['dev', 'local', 'production', ])
DEF_SYST_CHOICE = 'production'
ACTION_CHOICES = frozenset(['curl', 'report', 'retry-failing', 'scan', 'test', ])
SCRIPT_NAME = os.path.split(sys.argv[0])[-1]
DEBUG_OUTPUT, SILENT_MODE = False, False
TEST_CACHE_PAR = os.path.expanduser('~/.opentreeoflife/test-ot-ws')
TEST_ADDR_LIST = os.path.join(TEST_CACHE_PAR, 'test_addr.json')
SERVICE_CHOICES = ('taxonomy', 'tnrs')
DEFAULT_NUM_THREADS = 8
TEST_NAME_PREF = 'otwstest.'


def debug(msg):
    if DEBUG_OUTPUT:
        sys.stderr.write('{} debug: {}\n'.format(SCRIPT_NAME, msg))


def warn(msg):
    if not SILENT_MODE:
        sys.stderr.write('{} warn: {}\n'.format(SCRIPT_NAME, msg))


def write_test_list_to_store(iterable):
    if not os.path.exists(TEST_CACHE_PAR):
        os.makedirs(TEST_CACHE_PAR)
    write_as_json(iterable, TEST_ADDR_LIST, indent=2)


def default_fill_cache_with_scan_for_tests():
    tc = TestingConfig()
    file_func_pairs = tc.scan_for_services(list(SERVICE_CHOICES))
    write_test_list_to_store([i[0] for i in file_func_pairs])


def read_test_list_from_store():
    if not os.path.exists(TEST_ADDR_LIST):
        default_fill_cache_with_scan_for_tests()
    if not os.path.exists(TEST_ADDR_LIST):
        return []
    return json.load(codecs.open(TEST_ADDR_LIST, 'rU', encoding='utf-8'))


def get_full_test_list():
    x = read_test_list_from_store()
    if not x:
        # noinspection PyTypeChecker
        x = [i[0] for i in TestingConfig().scan_for_services(SERVICE_CHOICES)]
    lp = len(TEST_NAME_PREF)
    return [i[lp:] if i.startswith(TEST_NAME_PREF) else i for i in x]


def get_globbed_test_list():
    ftl = get_full_test_list()
    gts = set()
    for f in ftl:
        frag = f
        while True:
            if frag in gts:
                break
            gts.add(frag)
            di = frag.rfind('.')
            if di < 0:
                break
            frag = frag[:di]
    gtl = list(gts)
    gtl.sort()
    return gtl


EXPLICIT_API_VERSIONS = ('v2', 'v3')


def clean_test_addr(addr):
    return addr[len(TEST_NAME_PREF):] if addr.startswith(TEST_NAME_PREF) else addr


class TestingConfig(object):
    def __init__(self,
                 system_to_test=DEF_SYST_CHOICE,
                 noise_level=2,
                 num_threads=DEFAULT_NUM_THREADS,
                 api_versions=EXPLICIT_API_VERSIONS):
        global DEBUG_OUTPUT, SILENT_MODE
        self.system_to_test = system_to_test.lower()
        assert self.system_to_test in SYST_CHOICES
        self.noise_level = noise_level
        if self.noise_level >= 5:
            DEBUG_OUTPUT = True
        elif self.noise_level == 0:
            SILENT_MODE = True
        self.needs_newline = False
        self.num_threads = num_threads
        self._res_par = os.path.join(TEST_CACHE_PAR, system_to_test)
        if is_str_type(api_versions):
            api_versions = [api_versions]
        self._testing_versions = set(api_versions)

    def testing_api_version(self, api_version):
        return api_version in self._testing_versions

    def get_results_dir(self, addr):
        addr = clean_test_addr(addr)
        addr = '/'.join(addr.split('.')[:-1])
        res_dir = os.path.join(self._res_par, addr)
        if not os.path.exists(res_dir):
            try:
                os.makedirs(res_dir)
            except FileExistsError:
                pass
        return res_dir

    def as_arg_list(self):
        a = ['--system={}'.format(self.system_to_test),
             '--noise={}'.format(self.noise_level),
             ]
        return a

    def run_test(self, test_addr, test_func, test_results):
        outcome = test_results.spawning_test(self, test_addr)
        self.run_spawned_test(outcome, test_func)

    def run_spawned_test(self, outcome, test_func):
        try:
            test_func(outcome)
        except TestEarlyExit:
            pass
        except Exception:
            outcome.uncaught(traceback.format_exc())
        outcome.record(self)
        return outcome.succeeded

    def status_message(self, level, message):
        if self.noise_level >= level:
            sys.stderr.write(message)
            self.needs_newline = not message.endswith('\n')

    def flush(self, results):
        results.flush(self)
        if self.needs_newline:
            sys.stderr.write('\n')

    def configure_url(self, frag):
        while frag.startswith('/'):
            frag = frag[1:]
        while frag.endswith('/'):
            frag = frag[:-1]
        if self.system_to_test == 'production':
            return 'https://api.opentreeoflife.org/{}'.format(frag)
        if self.system_to_test == 'dev':
            return 'https://devapi.opentreeoflife.org/{}'.format(frag)
        if self.system_to_test == 'local':
            tax_pat = re.compile(r'^(v[0-9.]+)/([a-z]+)/(.+)$')
            m = tax_pat.match(frag)
            if m:
                vers, top_level, tail_frag = m.groups()
                if top_level in ('taxonomy', 'tnrs'):
                    t = 'http://localhost:7474/db/data/ext/{}_{}/graphdb/{}'
                    return t.format(top_level, vers, tail_frag)
            raise NotImplemented('non-taxonomy local system_to_test')
        assert False

    def iter_previous(self):
        if not os.path.exists(self._res_par):
            return
        vers_outcome_pat = re.compile(r'^(v[0-9.]+)_outcome\.json$')
        for d, sub, file_list in os.walk(self._res_par):
            for fn in file_list:
                if vers_outcome_pat.match(fn):
                    yield json.load(codecs.open(os.path.join(d, fn), 'rU', encoding='utf-8'))

    def scan_for_services(self, services):
        if not isinstance(services, list):
            services = list(services)
        services.sort()
        addr = TEST_NAME_PREF
        file_func_pairs = []
        # noinspection PyUnresolvedReferences
        import otwstest
        for s in services:
            x = _collect_file_func_pairs(otwstest.__dict__[s], addr + s, self._testing_versions)
            file_func_pairs.extend(x)
        return file_func_pairs


def _collect_file_func_pairs(mod_obj, addr, version_set=None):
    ret = []
    if not mod_obj.__name__.startswith('otwstest'):
        return ret
    for k, v in mod_obj.__dict__.items():
        if k.startswith('_'):
            continue
        extended = '{}.{}'.format(addr, k)
        if k.startswith('test'):
            try:
                vspec = v.api_versions
                for vstr in vspec:
                    if (version_set is None) or (vstr in version_set):
                        ret.append(('{}.{}'.format(extended, vstr), v))
            except Exception:
                m = '{} matches pattern, but lacks api_versions attribute.\n'.format(extended)
                sys.stderr.write(m)
        elif isinstance(v, types.ModuleType):
            ret.extend(_collect_file_func_pairs(v, extended, version_set=version_set))
    return ret


def _aug_comp_list_eq(opts_to_values, key, comp_list):
    vals = list(opts_to_values.get(key, []))
    vals.sort()
    # sys.stderr.write('\nkey = {} vals={}\n'.format(key, vals))
    comp_list.extend(['{}'.format(i) for i in vals])


def _aug_comp_list_eq_started(opts_to_values, key, val_start, comp_list):
    vals = opts_to_values.get(key, [])
    if val_start in vals:
        return True
    vals = list(vals)
    vals.sort()
    comp_list.extend([i for i in vals if i.startswith(val_start)])
    return False


def demand_property(prop, result, outcome, obj_type_name):
    if prop not in result:
        errstr = 'No "{}" property found in {} returned object.'.format(prop, obj_type_name)
        outcome.exit_test_with_failure(errstr)
    return result.get(prop)


def top_main(argv, deleg=None, nested=False):
    import argparse
    description = "Tests of web services for Open Tree of Life project"
    if deleg is not None:
        description += ' tests just from "{}"'.format(deleg)
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--show-completions",
                   action="store_true",
                   default=False,
                   help=argparse.SUPPRESS)
    p.add_argument("--version",
                   action="store_true",
                   default=False,
                   help='print version of the testing software and exit')
    p.add_argument("--noise",
                   default=3,
                   type=int,
                   required=False,
                   help='Controls level of output sent to standard error: 0=silent, '
                        '1=only numbers of outcomes, 2=progress and outcomes, '
                        '3(default)=brief message for each failure, 4=detailed messages, '
                        '5=trace level')
    p.add_argument("--threads",
                   default=DEFAULT_NUM_THREADS,
                   type=int,
                   required=False,
                   help='Controls number of threads used to spawn calls')
    p.add_argument('--action', choices=ACTION_CHOICES, default='test',
                   help='controls the main action. Default is "test" to run tests. "retry-failing" '
                        'runs only tests that have previously failed. "report" describes that '
                        'last run state of each test without re-executing any tests. "scan" is '
                        'only used by developers, it records the list of available tests for '
                        'better tab-completion. "curl" writes the curl version of a test\'s call '
                        'to standard output if the test has been run at least once.')
    p.add_argument('--system', choices=SYST_CHOICES, default=DEF_SYST_CHOICE,
                   help='Directs the tests to be run again the main (production) servers by '
                        'default. "dev" runs the test against the development servers, and '
                        '"local" tells the tests to run against the default endpoints used '
                        'by developers of Open Tree of Life when testing on their own '
                        'computers.')
    TEST_CHOICES = get_globbed_test_list()
    p.add_argument('--test', choices=TEST_CHOICES, default=None, required=False,
                   help='Specifies a prefix of a test name. All test names that start with that '
                        'prefix followed by a . will be matched and run')
    API_VERSION_CHOICES = ['v2', 'v3', 'all']
    p.add_argument('--api-version', choices=API_VERSION_CHOICES, default='all', required=False,
                   help='specifies which version of the API to test.')

    if deleg is None:
        p.add_argument('service', nargs='?', choices=SERVICE_CHOICES)
    tr = TestResults()
    if "--show-completions" in argv:
        DASHED_ARGUMENTLESS = ['--version', '--help']
        ARGUMENTLESS = DASHED_ARGUMENTLESS + list(SERVICE_CHOICES)
        try:
            a = argv[3:]
        except Exception:
            a = []
        # sys.stderr.write('\na={}\n'.format(a))
        opts_to_values = {'--api-version': API_VERSION_CHOICES,
                          '--noise': [str(i) for i in range(6)],
                          '--action': ACTION_CHOICES,
                          '--system': SYST_CHOICES,
                          '--test': TEST_CHOICES,
                          '--threads': [str(i) for i in range(20)],
                          }
        comp_list = []
        ov_end = len(a) == 0
        if not ov_end:
            last = a[-1]
            if last.startswith('-'):
                # completing an option
                assert '=' not in last
                for key, vals in opts_to_values.items():
                    if key.startswith(last) and key not in a:
                        comp_list.extend(['{}={}'.format(key, i) for i in vals])
                for s in DASHED_ARGUMENTLESS:
                    if s.startswith(last):
                        comp_list.append(s)
            elif last == '=':
                # = sign separating an option from its value.
                if len(a) > 1:
                    _aug_comp_list_eq(opts_to_values, a[-2], comp_list)
            elif len(a) > 2 and a[-2] == '=':
                # complete a the value in progress
                if _aug_comp_list_eq_started(opts_to_values, a[-3], last, comp_list):
                    ov_end = True
            else:
                for s in ARGUMENTLESS:
                    if s.startswith(last):
                        if s == last:
                            ov_end = True
                            break
                        else:
                            comp_list.append(s)
        if ov_end:
            for s in ARGUMENTLESS:
                if s not in a:
                    comp_list.append(s)
            for o in opts_to_values.keys():
                if o not in a:
                    comp_list.append(o)
        comp_list.extend(['-h', '--help'])
        sys.stdout.write('{}\n'.format(' '.join(comp_list)))
        # sys.stderr.write('\nfinal return: {}\n'.format(' '.join(comp_list)))
        return tr
    try:
        parsed = p.parse_args(args=argv[1:])
    except SystemExit:
        if (not nested) and not ('-h' in argv or '--help' in argv):
            default_fill_cache_with_scan_for_tests()
            return top_main(argv, deleg=deleg, nested=True)
        else:
            raise
    if parsed.version:
        print('{} using otwstest version {}'.format(SCRIPT_NAME, __version__))
        return tr
    v = parsed.api_version
    av = EXPLICIT_API_VERSIONS if v.lower() == 'all' else [v]
    tc = TestingConfig(system_to_test=parsed.system,
                       noise_level=parsed.noise,
                       num_threads=parsed.threads,
                       api_versions=av
                       )
    try:
        if deleg is None:
            # noinspection PyUnresolvedReferences
            s = parsed.service
            if isinstance(s, str):
                s = [s]
            file_func_pairs = tc.scan_for_services(list(s or SERVICE_CHOICES))
            addr_to_skip = []
            if parsed.action == 'retry-failing':
                for blob in tc.iter_previous():
                    if blob.get('status', '').upper() == 'SUCCESS':
                        addr_to_skip.append(blob['test_addr'])
            elif parsed.action == 'scan':
                write_test_list_to_store([i[0] for i in file_func_pairs])
                return tr
            else:
                addr_to_skip = frozenset(addr_to_skip)
                file_func_pairs = [i for i in file_func_pairs if i[0] not in addr_to_skip]
            if parsed.test is not None:
                test_glob = '{}{}'.format(TEST_NAME_PREF, parsed.test)
                try:
                    file_func_pairs = [i for i in file_func_pairs if i[0].startswith(test_glob)]
                except Exception:
                    pass
                if len(file_func_pairs) == 0:
                    sys.exit('No tests matched --test="{}"'.format(parsed.test))
            if parsed.action == 'report':
                _do_report_action(tc, file_func_pairs)
                return tr
            elif parsed.action == 'curl':
                _do_curl_action(tc, file_func_pairs)
                return tr
            run_tests(tc, file_func_pairs, tr)
        return tr
    finally:
        tc.flush(tr)


def _iter_addr_and_blob_for_prev_run(test_config, file_func_pairs):
    addr_2_blob = {}
    for blob in test_config.iter_previous():
        addr_2_blob[blob['test_addr']] = blob
    for i in file_func_pairs:
        addr = i[0]
        yield addr, addr_2_blob.get(addr)


def escape_dq(s):
    if not is_str_type(s):
        if isinstance(s, bool):
            return 'true' if s else 'false'
        return s
    if '"' in s:
        ss = s.split('"')
        return '"{}"'.format('\\"'.join(ss))
    return '"{}"'.format(s)


def write_test_as_curl(out, blob):
    for cblob in blob['calls']:
        write_call_as_curl(out, cblob)


def write_call_as_curl(out, cblob):
    v = cblob['verb']
    headers = cblob['headers']
    data = cblob['data']
    url = cblob['url']
    varg = '' if v == 'GET' else '-X {} '.format(v)
    if headers:
        hal = ['-H {}:{}'.format(escape_dq(k), escape_dq(v)) for k, v in headers.items()]
        hargs = ' '.join(hal)
    else:
        hargs = ''
    dargs = " --data '{}'".format(json.dumps(data)) if data else ''
    out.write('curl {v} {h} {u}{d}\n'.format(v=varg, u=url, h=hargs, d=dargs))


def _do_curl_action(test_config, file_func_pairs):
    for addr, blob in _iter_addr_and_blob_for_prev_run(test_config, file_func_pairs):
        if blob is None:
            warn('Test "{}" must be run before curl version can be generated.'.format(addr))
        else:
            write_test_as_curl(sys.stdout, blob)


def _do_report_action(test_config, file_func_pairs):
    by_status = {}
    for addr, blob in _iter_addr_and_blob_for_prev_run(test_config, file_func_pairs):
        if blob is None:
            by_status.setdefault('NOT_RECORDED', []).append(addr)
        else:
            by_status.setdefault(blob.get('status', 'UNKNOWN'), []).append(addr)
    status_sorted = [i for i in STATUS_REPORT_ORDER if i in by_status]
    for status in status_sorted:
        addr_list = by_status[status]
        for addr in addr_list:
            a = addr[len(TEST_NAME_PREF):] if addr.startswith(TEST_NAME_PREF) else addr
            print('{} {}'.format(a, status))
    print(' '.join(['#{}={}.'.format(i, len(by_status[i])) for i in status_sorted]))


from . import taxonomy, tnrs, schema
