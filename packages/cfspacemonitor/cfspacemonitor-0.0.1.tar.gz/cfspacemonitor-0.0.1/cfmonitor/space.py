import os
import sys
import time
import traceback
import logging
import cf_api
import importlib
import requests
import shlex
from threading import Thread, Event
from subprocess import Popen
from cf_api.deploy_space import Space as CFSpace
from cf_api.dropsonde_util import DopplerEnvelope, format_unixnano
from logging.handlers import TimedRotatingFileHandler
from websocket import WebSocketConnectionClosedException
from requests_factory import ResponseException

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(process)s - %(message)s'


def get_log_level(envname, default='DEBUG'):
    return getattr(logging,
                   os.getenv(envname, default).strip().upper(),
                   logging.DEBUG)


def get_logger(**kwargs):
    name = kwargs.get('name')
    filename = kwargs.get('filename')
    log_format = kwargs.get('log_format', LOG_FORMAT)
    when = kwargs.get('when', os.getenv('ROTATE_WHEN', 'midnight'))
    backup_count = kwargs.get(
        'backup_count', int(os.getenv('BACKUP_COUNT', 30)))

    filename = os.path.abspath(filename)
    dirname = os.path.dirname(filename)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(log_format)
        handler = TimedRotatingFileHandler(
            filename, when=when, backupCount=backup_count)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


class AppConfig(object):
    def __init__(self, name):
        self.name = os.getenv('APP_NAME', name)
        self.workspace = os.path.abspath(os.getenv('WORKSPACE', 'workspace'))
        self.deployment_name = os.getenv('CF_DEPLOYMENT')
        self.space_name = os.getenv('CF_SPACE')
        self.organization_name = os.getenv('CF_ORGANIZATION')
        self.application_name = os.getenv('CF_APPLICATION')
        self.application_guid = os.getenv('CF_APPLICATION_GUID')
        self.log_level = get_log_level('APP_LOG_LEVEL')
        self.rotate_when = os.getenv('APP_ROTATE_WHEN', 'midnight')
        self.backup_count = int(os.getenv('APP_BACKUP_COUNT', 0))
        self.log_filename_format = os.getenv(
            'APP_LOG_FILENAME_FORMAT',
            '{workspace}/apps/{application}/'
            '{deployment}_{organization}_{space}.log')
        self.logger = get_logger(
            name=self.name,
            filename=self.get_log_filename(),
            when=self.rotate_when,
            backup_count=self.backup_count)
        self.logger.setLevel(self.log_level)

    def validate(self):
        errors = []
        for key in ['deployment_name', 'space_name', 'organization_name',
                    'application_name', 'application_guid']:
            if not getattr(self, key):
                errors.append(key)
        if errors:
            raise Exception('Missing required settings: ' + ', '.join(errors))

    def get_log_filename(self):
        return self.log_filename_format.format(
            workspace=self.workspace,
            deployment=self.deployment_name,
            organization=self.organization_name,
            space=self.space_name,
            application=self.application_name,
        )

    def log_starting(self):
        self.logger.debug('Starting {0}...'.format(self.name))

    def log_started(self):
        self.logger.debug('Started {0}.'.format(self.name))
        self.logger.debug('Deployment:   {0}'.format(self.deployment_name))
        self.logger.debug('Organization: {0}'.format(self.organization_name))
        self.logger.debug('Space:        {0}'.format(self.space_name))
        self.logger.debug('Application:  {0}'.format(self.application_name))
        self.logger.debug('App GUID:     {0}'.format(self.application_guid))
        self.logger.debug('Rotation:     {0} keep {1} files'
                          .format(self.rotate_when, self.backup_count))

    def log_stopping(self):
        self.logger.debug('Stopping {0}...'.format(self.name))

    def log_stopped(self):
        self.logger.debug('Stopped {0}.'.format(self.name))


class Config(object):

    def __init__(self):
        self.name = os.getenv('SPACE_NAME')
        self.deployment_name = os.getenv('CF_DEPLOYMENT')
        self.space_name = os.getenv('CF_SPACE')
        self.organization_name = os.getenv('CF_ORGANIZATION')

        self.workspace = os.path.abspath(os.getenv('WORKSPACE', 'workspace'))
        self.refresh_interval = int(os.getenv('REFRESH_INTERVAL', 300))
        self.rotate_when = os.getenv('ROTATE_WHEN', 'midnight')
        self.backup_count = int(os.getenv('BACKUP_COUNT', 0))
        self.share_env = os.getenv('SHARE_ENV', '')

        self.space_log_level = get_log_level('SPACE_LOG_LEVEL', default='INFO')
        self.space_log_filename_format = os.getenv(
            'SPACE_LOG_FILENAME_FORMAT',
            '{workspace}/spaces/{space}/{deployment}_{organization}.log')
        self.app_script_name = shlex.split(os.getenv('APP_SCRIPT_NAME', ''))

    def validate(self):
        errors = []
        for key in ['deployment_name', 'space_name', 'organization_name',
                    'app_script_name']:
            if not getattr(self, key):
                errors.append(key)
        if errors:
            raise Exception('Missing required settings: ' + ', '.join(errors))

    def get_app_env(self, application_name, application_guid):
        env = {
            'WORKSPACE': self.workspace,
            'CF_DEPLOYMENT': self.deployment_name,
            'CF_ORGANIZATION': self.organization_name,
            'CF_SPACE': self.space_name,
            'CF_APPLICATION': application_name,
            'CF_APPLICATION_GUID': application_guid,}
        names = set([
            'APP_NAME',
            'APP_LOG_FILENAME_FORMAT',
            'APP_LOG_LEVEL',
            'APP_ROTATE_WHEN',
            'APP_BACKUP_COUNT'])
        if self.share_env:
            share = set([name.strip() for name in self.share_env.split(',')])
            names = names.union(share)
        for name in names:
            if name in os.environ:
                env[name] = os.getenv(name)
        return env

    def get_app_name(self, application_name):
        return '/'.join([self.deployment_name, self.organization_name,
                         self.space_name, application_name])

    def get_log_filename(self):
        return self.space_log_filename_format.format(
            workspace=self.workspace,
            deployment=self.deployment_name,
            organization=self.organization_name,
            space=self.space_name,
        )

    def get_space_logger(self):
        logger = get_logger(
            name='monitor.space',
            filename=self.get_log_filename(),
            when=self.rotate_when,
            backup_count=self.backup_count)
        logger.setLevel(self.space_log_level)
        return logger


class Space(object):
    space = None
    cc = None

    def __init__(self, config):
        self.pid = os.getpid()
        self.config = config
        self.processes = {}
        self.apps = {}
        self.logger = config.get_space_logger()
        self.is_stopping = Event()
        self.is_started = Event()

    def _reset_cc(self):
        self.logger.debug('Authenticating with Cloud Controller...')
        self.cc = cf_api.new_cloud_controller()
        self.space = CFSpace(self.cc, org_name=self.config.organization_name,
                             space_name=self.config.space_name)
        self.logger.debug('Authentication successful.')

    def _get_space(self):
        if self.cc is None:
            self._reset_cc()
        try:
            self.cc.refresh_tokens()
        except ResponseException as e:
            if '"invalid_token"' in str(e):
                self._reset_cc()
            else:
                raise
        return self.space

    def _refresh_space(self):
        self.logger.info('Refreshing space...')
        try:
            space = self._get_space()
            req = space.request('apps')
            apps = space.cc.get_all_resources(req)
        except requests.exceptions.ConnectionError as e:
            import traceback
            traceback.print_exc()
            self.logger.error(str(e))
            self.logger.error('Aborted refreshing space due to connection error.')
            return
        except ResponseException as e:
            if 'not found' in str(e).lower():
                self.logger.error(str(e))
                self.logger.error('Aborted refreshing space due to 404.')
                return
            elif 'internal server error' in str(e).lower():
                self.logger.error(str(e))
                self.logger.error('Aborted refreshing space due to error.')
                return
            else:
                raise
        apps = {
            app.guid: app.name
            for app in apps
            if 'STARTED' == app.state
        }
        curr_keys = set(apps.keys())
        last_keys = set(self.apps.keys())
        new_keys = curr_keys - last_keys
        dead_keys = last_keys - curr_keys
        self._stop_dead_apps(dead_keys)
        self.apps = apps
        self._start_new_apps(new_keys)
        self._restart_crashed_apps()
        self.logger.info('Refreshed space.')

    def _stop_dead_apps(self, dead_keys):
        if not dead_keys:
            return
        self.logger.info('Sending cleanup signal to dead apps...')
        self.logger.debug('Dead apps ' + self.get_names(dead_keys))
        for app_guid in dead_keys:
            self._signal_stop_app(app_guid)
        for app_guid in dead_keys:
            self._wait_stop_app(app_guid)
        self.logger.info('Sent cleanup signal to dead apps.')
        while len(dead_keys) > 0:
            self.logger.debug('Waiting for dead apps to exit... ' +
                              self.get_names(dead_keys))
            for app_guid in [k for k in dead_keys]:
                if self._cleanup_stopped_app(app_guid):
                    self.logger.debug('Stopped ' + self.get_name(app_guid))
                    dead_keys.remove(app_guid)
            time.sleep(5)
        self.logger.info('All dead apps have exited.')

    def _start_new_apps(self, new_keys):
        if not new_keys:
            return
        self.logger.info('Starting new apps...')
        self.logger.debug('New apps ' + ', '.join(new_keys))
        for app_guid in new_keys:
            if self._start_app(app_guid):
                self.logger.debug('Started ' + self.get_name(app_guid))
        self.logger.info('Started new apps.')

    def _restart_crashed_apps(self):
        self.logger.info('Restarting crashed apps...')
        for app_guid in self.processes.keys():
            if self._restart_app_if_stopped(app_guid):
                self.logger.debug('Restarted ' + self.get_name(app_guid))
        self.logger.info('Restarted crashed apps.')

    def _signal_stop_app(self, app_guid):
        if app_guid in self.processes:
            proc = self.processes[app_guid]
            proc.terminate()
#            proc.wait()
        return app_guid in self.processes

    def _wait_stop_app(self, app_guid):
        if app_guid in self.processes:
            proc = self.processes[app_guid]
            proc.wait()
        return app_guid in self.processes

    def _cleanup_stopped_app(self, app_guid):
        if app_guid in self.processes and self._is_app_stopped(app_guid):
            del self.processes[app_guid]
        return app_guid not in self.processes

    def _start_app(self, app_guid):
        if app_guid not in self.processes:
            self.processes[app_guid] = self._create_app_process(app_guid)
            return True
        return False

    def _is_app_stopped(self, app_guid):
        return self.processes[app_guid].returncode is not None

    def _restart_app_if_stopped(self, app_guid):
        if self._is_app_stopped(app_guid):
            del self.processes[app_guid]
            self._start_app(app_guid)
            return True
        return False

    def _create_app_process(self, app_guid):
        app_name = self.apps[app_guid]
        env = self.config.get_app_env(app_name, app_guid)
        args = []
        args.extend(self.config.app_script_name)
        args.extend([self.config.get_app_name(app_name)])
        proc = Popen(args, env=env)
        return proc

    def start_all(self):
        self.logger.debug('Started {0}.'.format(self.config.name))
        self.logger.debug('Deployment:   {0}'.format(self.config.deployment_name))
        self.logger.debug('Organization: {0}'.format(self.config.organization_name))
        self.logger.debug('Space:        {0}'.format(self.config.space_name))
        self.is_started.set()
        while not self.is_stopping.is_set():
            self._refresh_space()
            time.sleep(self.config.refresh_interval)

    def stop_all(self):
        self.is_stopping.set()
        self.logger.info('Signaling "STOP" to all apps...')
        for app_guid in self.processes.keys():
            self._signal_stop_app(app_guid)
        for app_guid in self.processes.keys():
            self._wait_stop_app(app_guid)
        self.logger.info('Waiting for all apps to exit... ')
        while len(self.processes) > 0:
            app_guids = set([k for k in self.processes.keys()])
            self.logger.debug('Stopping apps... ' + self.get_names(app_guids))
            for app_guid in [k for k in app_guids]:
                if self._cleanup_stopped_app(app_guid):
                    self.logger.debug('Stopped ' + self.get_name(app_guid))
                    app_guids.remove(app_guid)
            time.sleep(1)
        self.logger.info('All apps stopped.')

    def get_name(self, app_guid):
        if app_guid in self.processes:
            proc = self.processes[app_guid]
            app_name = self.apps[app_guid]
            return '{0} ({1})'.format(
                self.config.get_app_name(app_name), proc.pid)
        return self.config.get_app_name(app_guid)

    def get_names(self, app_guids):
        return os.linesep + os.linesep.join([
            self.get_name(app_guid) for app_guid in app_guids])


def main():
    import signal
    config = Config()
    config.validate()
    space = Space(config)

    def handler(signum, handler):
        space.stop_all()

    signal.signal(signal.SIGTERM, handler)

    space.start_all()


if '__main__' == __name__:
    main()
