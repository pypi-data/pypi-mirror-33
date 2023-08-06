import os
import re
import time
import shutil
import logging
import threading
import subprocess
import responses
from cfmonitor.space import *
from cf_api.deploy_space import Space as CFSpace
from unittest import TestCase
from mock_cf import *


app_name = 'app_example'
space_name = 'space_example'
dep = 'test_d'
org = 'test_o'
space = 'test_s'
app = 'test_a'
guid = 'test_guid'
log_level = 'error'
when = 'midnight'
backup = 1
workspace_dir = os.path.abspath('test-workspace')
testlogger_file = os.path.abspath('test/testlogger.txt')

cf = CF(**{
    'guid': guid,
    'organization_name': org,
    'space_name': space,
    'app_name': app,
    'organization_guid': guid,
    'space_guid': guid,
    'app_guid': guid,
})

variables = [
    'PYTHONPATH',
    'APP_NAME',
    'SPACE_NAME',
    'WORKSPACE',
    'CF_DEPLOYMENT',
    'CF_ORGANIZATION',
    'CF_SPACE',
    'APP_SCRIPT_NAME',
    'MY_LOG_LEVEL',
    'CF_APPLICATION',
    'CF_APPLICATION_GUID',
    'APP_ROTATE_WHEN',
    'APP_BACKUP_COUNT',
    'APP_LOG_FILENAME_FORMAT',
    'APP_LOG_LEVEL',
    'WHOSTARTED',
]


def cleanup_workspace():
    if os.path.isdir(workspace_dir):
        shutil.rmtree(workspace_dir)
    if os.path.isfile(testlogger_file):
        os.remove(testlogger_file)


def find_patterns_in_file(filename, patterns):
    patterns = set(patterns)
    found = set()
    with open(filename) as f:
        for line in f:
            for pattern in patterns:
#                print('comparing', pattern, line, re.search(pattern, line, flags=re.I))
                if re.search(pattern, line, flags=re.I):
                    found.add(pattern)
                    break
#        print(found)
    return len(patterns - found) == 0


def whostarted(func):

    def test_wrapper(self):
        os.environ['WHOSTARTED'] = func.__name__
        return func(self)

    return test_wrapper


def del_variables():
    for name in variables:
        if name in os.environ:
            del os.environ[name]


def get_app_config():
    return dict(
        WORKSPACE=workspace_dir,
        CF_DEPLOYMENT=dep,
        CF_ORGANIZATION=org,
        CF_SPACE=space,
        CF_APPLICATION=app,
        CF_APPLICATION_GUID=guid,
        APP_LOG_LEVEL=log_level,
        APP_ROTATE_WHEN=when,
        APP_BACKUP_COUNT=str(backup),
    )


def get_space_config():
    return dict(
        SPACE_NAME=space_name,
        SPACE_LOG_LEVEL=log_level,
        WORKSPACE=workspace_dir,
        CF_DEPLOYMENT=dep,
        CF_ORGANIZATION=org,
        CF_SPACE=space,
        APP_SCRIPT_NAME='python -m cfmonitor.example',
        PYTHON_CF_URL=cf_base_url,
        PYTHON_CF_CLIENT_ID='client-id',
        PYTHON_CF_CLIENT_SECRET='client-secret',
        SHARE_ENV='WHOSTARTED',
    )


class Module(TestCase):

    def test_get_log_level(self):
        os.environ['MY_LOG_LEVEL'] = 'ERROR'
        level = get_log_level('MY_LOG_LEVEL')
        self.assertEqual(logging.ERROR, level)
        del os.environ['MY_LOG_LEVEL']

    def test_get_logger(self):
        logger = get_logger(name='testlogger', filename=testlogger_file)
        self.assertIsInstance(logger, logging.Logger)


class TestAppConfig(TestCase):
    def tearDown(self):
        del_variables()

    def test_init(self):
        self.assertNotIn('APP_NAME', os.environ)
        os.environ.update(get_app_config())
        config = AppConfig(app_name)
        self.assertEqual(config.name, app_name)
        self.assertEqual(config.workspace, workspace_dir)
        self.assertEqual(config.deployment_name, dep)
        self.assertEqual(config.organization_name, org)
        self.assertEqual(config.space_name, space)
        self.assertEqual(config.application_name, app)
        self.assertEqual(config.application_guid, guid)
        self.assertEqual(config.logger.level, logging.ERROR)
        self.assertEqual(config.rotate_when, when)
        self.assertEqual(config.backup_count, backup)

    def test_validate(self):
        os.environ.update(get_app_config())
        config = AppConfig(app_name)
        config.validate()

    def test_get_log_filename(self):
        os.environ.update(get_app_config())
        config = AppConfig(app_name)
        fn1 = config.get_log_filename()
        fn2 = os.path.join(workspace_dir, 'apps/test_a/test_d_test_o_test_s.log')
        self.assertEqual(fn1, fn2)


class TestConfig(TestCase):
    def tearDown(self):
        del_variables()

    def test_init(self):
        os.environ.update(get_space_config())
        config = Config()
        self.assertEqual(config.name, space_name)
        self.assertEqual(config.deployment_name, dep)
        self.assertEqual(config.organization_name, org)
        self.assertEqual(config.space_name, space)
        self.assertEqual(config.workspace, workspace_dir)

    def test_validate(self):
        os.environ.update(get_space_config())
        config = Config()
        config.validate()

    def test_get_app_env(self):
        os.environ.update(get_space_config())
        config = Config()
        env = config.get_app_env(app, guid)
        self.assertDictEqual(env, {
            'WORKSPACE': workspace_dir,
            'CF_DEPLOYMENT': dep,
            'CF_ORGANIZATION': org,
            'CF_SPACE': space,
            'CF_APPLICATION': app,
            'CF_APPLICATION_GUID': guid,
        })

    def test_get_app_name(self):
        os.environ.update(get_space_config())
        config = Config()
        name = config.get_app_name(app)
        self.assertEqual(name, 'test_d/test_o/test_s/test_a')

    def test_get_log_filename(self):
        os.environ.update(get_space_config())
        config = Config()
        fn1 = config.get_log_filename()
        fn2 = os.path.join(workspace_dir, 'spaces/test_s/test_d_test_o.log')
        self.assertEqual(fn1, fn2)

    def test_get_space_logger(self):
        os.environ.update(get_space_config())
        config = Config()
        logger = config.get_space_logger()
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.level, logging.ERROR)


class TestSpace(TestCase):
    space = None

    def setUp(self):
        os.environ.update(get_space_config())

    def tearDown(self):
        if self.space is not None:
            self.space.stop_all()
        del_variables()
        cleanup_workspace()

    @responses.activate
    def test_get_space(self):
        get_info()
        post_token()
        cf.expect_search_resources('organizations', org)
        cf.expect_search_resource_resources('organizations', guid, 'spaces', space)
        self.config = Config()
        self.space = Space(self.config)
        self.space._get_space()
        self.assertIsInstance(self.space.space, CFSpace)

    @responses.activate
    @whostarted
    def test_refresh_space(self):
        get_info()
        post_token()
        cf.expect_search_resources('organizations', org)
        cf.expect_search_resource_resources('organizations', guid, 'spaces', space, space)
        cf.expect_get_resource_resources('spaces', space, 'apps', app)

        self.config = Config()
        self.space = Space(self.config)
        self.assertDictEqual(self.space.apps, {})
        self.space._refresh_space()
        self.assertDictEqual(self.space.apps, {'test_a': 'thing-0'})
        self.assertGreater(len(self.space.apps), 0)
        for guid_, proc in self.space.processes.items():
            self.assertIsInstance(proc, subprocess.Popen)
            self.assertIsNone(proc.returncode)
        l1 = set([k for k in self.space.apps.keys()])
        l2 = set([k for k in self.space.processes.keys()])
        self.assertEqual(len(l1 - l2), 0)
        self.assertEqual(len(l2 - l1), 0)

    @whostarted
    def test_stop_dead_apps(self):
        self.config = Config()
        self.space = Space(self.config)
        self.space.apps = {app: 'thing-0'}
        self.space._start_new_apps([app])
        self.assertIn(app, self.space.processes)
        time.sleep(1)
        self.space._stop_dead_apps([app])
        self.assertNotIn(app, self.space.processes)

    @whostarted
    def test_start_new_apps(self):
        self.config = Config()
        self.space = Space(self.config)
        self.space.apps = {app: 'thing-0'}
        self.space._start_new_apps([app])
        self.assertIn(app, self.space.processes)

    @whostarted
    def test_restart_crashed_apps(self):
        self.config = Config()
        self.space = Space(self.config)
        self.space.apps = {app: 'thing-0'}
        self.space._start_new_apps([app])
        proc = self.space.processes[app]
        pid = proc.pid
        proc.terminate()
        proc.wait()
        self.space._restart_crashed_apps()
        self.assertIn(app, self.space.processes)
        proc = self.space.processes[app]
        self.assertNotEqual(pid, proc.pid)
        self.space._signal_stop_app(app)
        self.space._cleanup_stopped_app(app)

    @whostarted
    def test_signal_stop_app(self):
        self.config = Config()
        self.space = Space(self.config)
        self.space.apps = {app: 'thing-0'}
        self.space._start_new_apps([app])
        proc = self.space.processes[app]
        self.space._signal_stop_app(app)
        self.assertIn(app, self.space.processes)
        self.assertIsInstance(self.space.processes[app].pid, int)
        self.space._cleanup_stopped_app(app)

    @whostarted
    def test_cleanup_stopped_app(self):
        self.config = Config()
        self.space = Space(self.config)
        self.space.apps = {app: 'thing-0'}
        self.space._start_new_apps([app])
        proc = self.space.processes[app]
        self.space._signal_stop_app(app)
        self.assertIn(app, self.space.processes)
        self.assertIsInstance(self.space.processes[app].pid, int)
        self.space._wait_stop_app(app)
        self.space._cleanup_stopped_app(app)
        self.assertNotIn(app, self.space.processes)

    @whostarted
    def test_start_app(self):
        self.config = Config()
        self.space = Space(self.config)
        self.space.apps = {app: 'thing-0'}
        self.assertNotIn(app, self.space.processes)
        self.space._start_app(app)
        self.assertIn(app, self.space.processes)
        self.space._signal_stop_app(app)
        self.space._cleanup_stopped_app(app)

    @whostarted
    def test_app_logs(self):
        self.config = Config()
        self.space = Space(self.config)
        self.space.apps = {app: app}
        self.assertNotIn(app, self.space.processes)
        self.space._start_app(app)
        self.assertIn(app, self.space.processes)

        os.environ.update(get_app_config())
        proc = self.space.processes[app]
        config = AppConfig(app_name)
        filename = config.get_log_filename()
        while not os.path.isfile(filename) or os.stat(filename).st_size == 0:
            time.sleep(1)
        self.space._signal_stop_app(app)
        self.space._cleanup_stopped_app(app)

        patterns = ['Starting', 'Started', 'Stopping', 'Stopped']
        self.assertTrue(find_patterns_in_file(filename, [
            '{0} - {1}'.format(proc.pid, name) for name in patterns]))

    @whostarted
    def test_is_app_stopped(self):
        self.config = Config()
        self.space = Space(self.config)
        self.space.apps = {app: 'thing-0'}
        self.assertNotIn(app, self.space.processes)
        self.space._start_app(app)
        self.assertFalse(self.space._is_app_stopped(app))
        self.space._signal_stop_app(app)
        self.space._wait_stop_app(app)
        self.assertTrue(self.space._is_app_stopped(app))
        self.space._cleanup_stopped_app(app)

    @whostarted
    def test_restart_app_if_stopped(self):
        self.config = Config()
        self.space = Space(self.config)
        self.space.apps = {app: 'thing-0'}
        self.assertNotIn(app, self.space.processes)
        self.space._start_app(app)
        proc = self.space.processes[app]
        pid1 = proc.pid
        self.assertFalse(self.space._is_app_stopped(app))
        proc.terminate()
        proc.wait()
        self.assertTrue(self.space._is_app_stopped(app))
        self.space._restart_app_if_stopped(app)
        self.assertFalse(self.space._is_app_stopped(app))
        pid2 = self.space.processes[app].pid
        self.assertNotEqual(pid1, pid2)
        self.space._cleanup_stopped_app(app)

    @whostarted
    def test_create_app_process(self):
        self.config = Config()
        self.space = Space(self.config)
        self.space.apps = {app: 'thing-0'}
        proc = self.space._create_app_process(app)
        self.assertIsInstance(proc, subprocess.Popen)
        proc.terminate()

    def test_start_and_stop_all(self):
        self.config = Config()
        self.space = Space(self.config)

        @responses.activate
        def run_start_all():
            get_info()
            post_token()
            cf.expect_search_resources('organizations', org)
            cf.expect_search_resource_resources('organizations', guid, 'spaces', space, space)
            cf.expect_get_resource_resources('spaces', space, 'apps', app)

            self.space.start_all()

        t = threading.Thread(target=run_start_all)
        t.daemon = True
        t.start()
        while len(self.space.processes) == 0 or not self.space.is_started.is_set():
            time.sleep(1)
        self.space.stop_all()

    def test_get_name(self):
        self.config = Config()
        self.space = Space(self.config)
        name = self.space.get_name(app)
        self.assertEqual(name, '/'.join([dep, org, space, app]))
        self.space.apps = {app: 'thing-0'}
        self.space._start_app(app)
        name = self.space.get_name(app)
        proc = self.space.processes[app]
        self.assertEqual(
            name, '{0} ({1})'.format('/'.join([
                dep, org, space, self.space.apps[app]]), proc.pid))

    def test_get_names(self):
        self.config = Config()
        self.space = Space(self.config)
        name = self.space.get_names([app])
        self.assertEqual(name, os.linesep + 'test_d/test_o/test_s/test_a')
