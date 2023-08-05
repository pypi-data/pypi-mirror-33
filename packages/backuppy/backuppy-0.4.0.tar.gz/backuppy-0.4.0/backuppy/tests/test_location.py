import os
import socket
import subprocess
from logging import getLogger
from unittest import TestCase
from paramiko import SSHException, SSHClient, PKey

from backuppy.location import PathLocation, SshTarget, FirstAvailableTarget, _new_snapshot_args, PathTarget, AskPolicy
from backuppy.notifier import Notifier
from backuppy.tests import SshLocationContainer

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory


class NewSnapshotArgsTest(TestCase):
    def test_new_snapshot_args(self):
        snapshot_name = 'foo_bar'
        with TemporaryDirectory() as path:
            for args in _new_snapshot_args(snapshot_name):
                subprocess.check_call(args, cwd=path)
            self.assertTrue(os.path.exists('/'.join([path, snapshot_name])))
            self.assertTrue(os.path.exists('/'.join([path, 'latest'])))


class PathLocationTest(TestCase):
    class PathLocation(PathLocation):
        def snapshot(self, name):
            pass

        def to_rsync(self):
            pass

    def test_is_available(self):
        logger = getLogger(__name__)
        notifier = Mock(Notifier)
        path = '/tmp'
        sut = self.PathLocation(logger, notifier, path)
        self.assertTrue(sut.is_available())

    def test_is_available_unavailable(self):
        logger = getLogger(__name__)
        notifier = Mock(Notifier)
        path = '/tmp/SomeNoneExistentPath'
        sut = self.PathLocation(logger, notifier, path)
        self.assertFalse(sut.is_available())


class PathTargetTest(TestCase):
    def test_to_rsync(self):
        logger = getLogger(__name__)
        notifier = Mock(Notifier)
        path = '/var/cache'
        sut = PathTarget(logger, notifier, path)
        self.assertEquals(sut.to_rsync(), '/var/cache/latest/')

    def test_snapshot_without_name(self):
        logger = getLogger(__name__)
        notifier = Mock(Notifier)
        with TemporaryDirectory() as path:
            sut = PathTarget(logger, notifier, path)
            sut.snapshot('foo')
            self.assertTrue(os.path.exists('/'.join([path, 'latest'])))

    def test_snapshot_should_rebuild_latest_symlink(self):
        snapshot_1_name = 'foo-bar'
        snapshot_2_name = 'BAZ_QUX'
        logger = getLogger(__name__)
        notifier = Mock(Notifier)
        with TemporaryDirectory() as path:
            sut = PathTarget(logger, notifier, path)
            sut.snapshot(snapshot_1_name)
            sut.snapshot(snapshot_2_name)
            latest_snapshot_path = subprocess.check_output(['readlink', '-f', '/'.join([path, 'latest'])]).decode(
                'utf-8').strip()
            self.assertTrue(os.path.exists('/'.join([path, 'latest'])))
            self.assertTrue(os.path.exists('/'.join([path, snapshot_1_name])))
            self.assertTrue(os.path.exists('/'.join([path, snapshot_2_name])))
            self.assertEquals(latest_snapshot_path,
                              '/'.join([path, snapshot_2_name]))


class AskPolicyTest(TestCase):
    @patch('backuppy.cli.input._input')
    def test_ask_confirm_yes_should_accept(self, m_input):
        sut = AskPolicy()
        m_input.side_effect = lambda *args: 'y'
        client = Mock(SSHClient)
        hostname = 'example.com'
        key = Mock(PKey)
        key.get_fingerprint.side_effect = lambda *args: b'foo'
        sut.missing_host_key(client, hostname, key)

    @patch('backuppy.cli.input._input')
    def test_ask_confirm_no_should_reject(self, m_input):
        sut = AskPolicy()
        m_input.side_effect = lambda *args: 'n'
        client = Mock(SSHClient)
        hostname = 'example.com'
        key = Mock(PKey)
        key.get_fingerprint.side_effect = lambda *args: b'foo'
        with self.assertRaises(SSHException):
            sut.missing_host_key(client, hostname, key)


class SshTargetTest(TestCase):
    def test_to_rsync(self):
        notifier = Mock(Notifier)
        user = 'bart'
        host = 'example.com'
        port = 666
        path = '/var/cache'
        sut = SshTarget(notifier, user, host, path, port)
        expected = 'bart@example.com:/var/cache/latest/'
        self.assertEquals(sut.to_rsync(), expected)

    def test_ssh_options(self):
        notifier = Mock(Notifier)
        user = 'bart'
        host = 'example.com'
        port = 666
        path = '/var/cache'
        sut = SshTarget(notifier, user, host, path, port)
        expected_ssh_options = {
            'IdentityFile': None,
            'Port': str(port),
            'StrictHostKeyChecking': 'yes',
            'UserKnownHostsFile': None,
        }
        self.assertEquals(
            sut.ssh_options(), expected_ssh_options)

    @patch('paramiko.SSHClient', autospec=True)
    def test_is_available(self, m):
        notifier = Mock(Notifier)
        user = 'bart'
        host = 'example.com'
        port = 666
        path = '/var/cache'
        sut = SshTarget(notifier, user, host, path, port)
        self.assertTrue(sut.is_available())
        self.assertNotEquals([], m.return_value.connect.mock_calls)
        m.return_value.connect.assert_called_with(host, port, user, timeout=9)

    @patch('paramiko.SSHClient', autospec=True)
    def test_is_available_connection_error(self, m):
        m.return_value.connect = Mock(side_effect=SSHException)
        notifier = Mock(Notifier)
        user = 'bart'
        host = 'example.com'
        port = 666
        path = '/var/cache'
        sut = SshTarget(notifier, user, host, path, port)
        self.assertFalse(sut.is_available())
        self.assertNotEquals([], m.return_value.connect.mock_calls)
        m.return_value.connect.assert_called_with(host, port, user, timeout=9)

    @patch('paramiko.SSHClient', autospec=True)
    def test_is_available_connection_timeout(self, m):
        m.return_value.connect = Mock(side_effect=socket.timeout)
        notifier = Mock(Notifier)
        user = 'bart'
        host = 'example.com'
        port = 666
        path = '/var/cache'
        sut = SshTarget(notifier, user, host, path, port)
        self.assertFalse(sut.is_available())
        self.assertNotEquals([], m.return_value.connect.mock_calls)
        m.return_value.connect.assert_called_with(host, port, user, timeout=9)

    @patch('paramiko.SSHClient', autospec=True)
    def test_snapshot_without_name(self, m):
        snapshot_name = 'foo_bar'
        notifier = Mock(Notifier)
        user = 'bart'
        host = 'example.com'
        port = 666
        path = '/var/cache'
        sut = SshTarget(notifier, user, host, path, port)
        sut.snapshot(snapshot_name)
        m.return_value.connect.assert_called_with(host, port, user, timeout=9)
        for args in _new_snapshot_args(snapshot_name):
            m.return_value.__enter__().exec_command.assert_any_call(' '.join(args))


class SshTargetIntegrationTest(TestCase):
    def setUp(self):
        self._container = SshLocationContainer()
        self._container.start()

    def tearDown(self):
        self._container.stop()

    def test_is_available(self):
        notifier = Mock(Notifier)
        path = '/var/cache'
        with self._container.known_hosts() as f:
            sut = SshTarget(notifier, self._container.USERNAME, self._container.ip, path,
                            self._container.PORT, identity=self._container.IDENTITY, host_keys=f.name)
            self.assertTrue(sut.is_available())

    def test_snapshot_without_name(self):
        snapshot_name = 'foo_bar'
        notifier = Mock(Notifier)
        path = '/var/cache'
        with self._container.known_hosts() as f:
            sut = SshTarget(notifier, self._container.USERNAME, self._container.ip, path,
                            self._container.PORT, identity=self._container.IDENTITY, host_keys=f.name)
            sut.snapshot(snapshot_name)


class FirstAvailableTargetTest(TestCase):
    def test_to_rsync(self):
        logger = getLogger(__name__)
        notifier = Mock(Notifier)
        target_1 = PathTarget(logger, notifier, '/tmp/SomeNoneExistentPath')
        target_2 = PathTarget(logger, notifier, '/tmp')
        target_3 = PathTarget(logger, notifier, '/tmp')
        sut = FirstAvailableTarget([target_1, target_2, target_3])
        self.assertEquals(sut.to_rsync(), target_2.to_rsync())
        # Try again, so we cover the SUT's internal static cache.
        self.assertEquals(sut.to_rsync(), target_2.to_rsync())

    def test_snapshot(self):
        snapshot_name = 'Foo_BAR'
        logger = getLogger(__name__)
        notifier = Mock(Notifier)
        target_1 = PathTarget(logger, notifier, '/tmp/SomeNoneExistentPath')
        target_2 = Mock(PathTarget)
        target_3 = PathTarget(logger, notifier, '/tmp')
        sut = FirstAvailableTarget([target_1, target_2, target_3])
        sut.snapshot(snapshot_name)
        target_2.snapshot.assert_called_with(snapshot_name)
        # Try again, so we cover the SUT's internal static cache.
        sut.snapshot(snapshot_name)
        target_2.snapshot.assert_called_with(snapshot_name)

    def test_is_available(self):
        logger = getLogger(__name__)
        notifier = Mock(Notifier)
        target_1 = PathTarget(logger, notifier, '/tmp/SomeNoneExistentPath')
        target_2 = PathTarget(logger, notifier, '/tmp')
        target_3 = PathTarget(logger, notifier, '/tmp')
        sut = FirstAvailableTarget([target_1, target_2, target_3])
        self.assertTrue(sut.is_available())
        # Try again, so we cover the SUT's internal static cache.
        self.assertTrue(sut.is_available())

    def test_is_available_unavailable(self):
        logger = getLogger(__name__)
        notifier = Mock(Notifier)
        target_1 = PathTarget(logger, notifier, '/tmp/SomeNoneExistentPath')
        target_2 = PathTarget(logger, notifier, '/tmp/SomeNoneExistentPath')
        target_3 = PathTarget(logger, notifier, '/tmp/SomeNoneExistentPath')
        sut = FirstAvailableTarget([target_1, target_2, target_3])
        self.assertFalse(sut.is_available())
        # Try again, so we cover the SUT's internal static cache.
        self.assertFalse(sut.is_available())
