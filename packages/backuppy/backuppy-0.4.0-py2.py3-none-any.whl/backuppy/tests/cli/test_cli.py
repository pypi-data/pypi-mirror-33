import json
import os
import subprocess
from logging import Logger, NOTSET
from tempfile import NamedTemporaryFile
from unittest import TestCase

from parameterized import parameterized

try:
    from unittest.mock import patch, call, Mock
except ImportError:
    from mock import patch, call, Mock

try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory

from backuppy.cli.cli import main, FORMAT_JSON_EXTENSIONS, FORMAT_YAML_EXTENSIONS
from backuppy.config import from_json, from_yaml
from backuppy.location import PathSource, PathTarget
from backuppy.tests import CONFIGURATION_PATH


class CliTest(TestCase):
    def test_help_appears_in_readme(self):
        """Assert that the CLI command's help output in README.md is up-to-date."""
        cli_help = subprocess.check_output(
            ['backuppy', '--help']).decode('utf-8')
        readme_path = os.path.join(os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'README.md')
        with open(readme_path) as f:
            self.assertIn(cli_help, f.read())

    def test_call_without_subcommand_or_arguments_prints_help(self):
        """Assert that the CLI command prints its help if it does not know what to do."""
        output_with_help = subprocess.check_output(
            ['backuppy', '--help']).decode('utf-8')
        output_without_arguments = subprocess.check_output(
            ['backuppy']).decode('utf-8')
        self.assertEquals(output_without_arguments, output_with_help)


class CliRestoreTest(TestCase):
    @patch('sys.stdout')
    @patch('sys.stderr')
    def test_restore_without_arguments(self, m_stdout, m_stderr):
        args = ['restore']
        with self.assertRaises(SystemExit):
            main(args)

    @patch('sys.stdout')
    @patch('sys.stderr')
    @patch('backuppy.task.restore')
    def test_keyboard_interrupt_in_command_should_exit_gracefully(self, m_restore, m_stderr, m_stdout):
        m_restore.side_effect = KeyboardInterrupt
        configuration_file_path = '%s/backuppy.json' % CONFIGURATION_PATH
        args = ['restore', '--non-interactive', '-c', configuration_file_path]
        main(args)
        m_stdout.write.assert_has_calls([call('Quitting...')])
        m_stderr.write.assert_not_called()

    @parameterized.expand([
        (ValueError,),
        (RuntimeError,),
        (AttributeError,),
        (ImportError,),
        (NotImplementedError,),
    ])
    @patch('sys.stdout')
    @patch('sys.stderr')
    @patch('backuppy.task.restore')
    @patch('logging.getLogger')
    def test_error_in_command(self, error_type, m_get_logger, m_restore, m_stderr, m_stdout):
        m_restore.side_effect = error_type
        m_logger = Mock(Logger)
        m_logger.handlers = Mock(side_effect=lambda: [])
        m_logger.getEffectiveLevel.side_effect = Mock(
            side_effect=lambda: NOTSET)
        m_get_logger.return_value = m_logger
        with open('%s/backuppy.json' % CONFIGURATION_PATH) as f:
            configuration = json.load(f)
        configuration['notifications'] = [
            {
                'type': 'stdio',
            }
        ]
        with NamedTemporaryFile(mode='w+t', suffix='.json') as f:
            json.dump(configuration, f)
            f.seek(0)
            args = ['restore', '--non-interactive', '-c', f.name]
            main(args)
            m_get_logger.assert_called_with('backuppy')
            self.assertTrue(m_logger.exception.called)
            m_stderr.write.assert_has_calls([
                call(
                    '\x1b[0;41m  \x1b[0;1;31m A fatal error occurred. Details have been logged as per your configuration.\x1b[0m'),
            ])


class CliInitTest(TestCase):
    @parameterized.expand([
        (True, 'yaml'),
        (True, 'yaml'),
        (False, 'json'),
        (False, 'json'),
    ])
    @patch('backuppy.cli.input._input')
    @patch('sys.stdout')
    @patch('sys.stderr')
    def test_init(self, verbose, format, m_stderr, m_stdout, m_input):
        name = 'Home is where the Bart is'
        source_path = '/tmp/Foo/Baz_bar_source'
        target_path = '/tmp/Foo/Baz_bar_target'
        with TemporaryDirectory() as working_directory:
            configuration_file_path = os.path.join(
                working_directory, 'backuppy.' + format)
            file_path_extensions = FORMAT_YAML_EXTENSIONS if 'yaml' == format else FORMAT_JSON_EXTENSIONS
            file_path_extensions_label = ', '.join(
                map(lambda x: '*.' + x, file_path_extensions))
            m_input.side_effect = lambda *args: {
                ('Name: ',): name,
                ('Verbose output [Y/n]: ',): 'y' if verbose else 'n',
                ('File format (0-1): ',): '0' if 'yaml' == format else '1',
                ('Destination (%s): ' % file_path_extensions_label,): configuration_file_path,
                ('Source path: ',): source_path,
                ('Target path: ',): target_path,
            }[args]
            args = ['init']
            main(args)
            with open(configuration_file_path) as f:
                factory = from_yaml if 'yaml' == format else from_json
                configuration = factory(f)
                self.assertEquals(configuration.name, name)
                self.assertEquals(configuration.verbose, verbose)
                source = configuration.source
                self.assertIsInstance(source, PathSource)
                self.assertEquals(source.path, source_path)
                target = configuration.target
                self.assertIsInstance(target, PathTarget)
                self.assertEquals(target.path, target_path)
