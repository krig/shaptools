"""
Unitary tests for hana.py.

:author: xarbulu
:organization: SUSE Linux GmbH
:contact: xarbulu@suse.com

:since: 2018-11-16
"""

# pylint:disable=C0103,C0111,W0212,W0611

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
import unittest
import filecmp
import shutil

try:
    from unittest import mock
except ImportError:
    import mock

from shaptools import hana

class TestHana(unittest.TestCase):
    """
    Unitary tests for hana.py.
    """

    @classmethod
    def setUpClass(cls):
        """
        Global setUp.
        """

        logging.basicConfig(level=logging.INFO)

    def setUp(self):
        """
        Test setUp.
        """
        self._hana = hana.HanaInstance('prd', '00', 'pass')

    def tearDown(self):
        """
        Test tearDown.
        """

    @classmethod
    def tearDownClass(cls):
        """
        Global tearDown.
        """

    def test_init(self):
        with self.assertRaises(TypeError) as err:
            self._hana = hana.HanaInstance(1, '00', 'pass')

        self.assertTrue(
            'provided sid, inst and password parameters must be str type' in
            str(err.exception))

        with self.assertRaises(TypeError) as err:
            self._hana = hana.HanaInstance('prd', 0, 'pass')

        self.assertTrue(
            'provided sid, inst and password parameters must be str type' in
            str(err.exception))

        with self.assertRaises(TypeError) as err:
            self._hana = hana.HanaInstance('prd', '00', 1234)

        self.assertTrue(
            'provided sid, inst and password parameters must be str type' in
            str(err.exception))


    @mock.patch('shaptools.shell.execute_cmd')
    def test_run_hana_command(self, mock_execute):
        proc_mock = mock.Mock()
        proc_mock.returncode = 0

        mock_execute.return_value = proc_mock

        result = self._hana._run_hana_command('test command')

        mock_execute.assert_called_once_with('test command', 'prdadm', 'pass')
        self.assertEqual(proc_mock, result)

    @mock.patch('shaptools.shell.execute_cmd')
    def test_run_hana_command_error(self, mock_execute):
        proc_mock = mock.Mock()
        proc_mock.returncode = 1
        proc_mock.cmd = 'updated command'

        mock_execute.return_value = proc_mock
        with self.assertRaises(hana.HanaError) as err:
            self._hana._run_hana_command('test command')

        mock_execute.assert_called_once_with('test command', 'prdadm', 'pass')
        self.assertTrue(
            'Error running hana command: {}'.format(
                'updated command') in str(err.exception))

    @mock.patch('shaptools.shell.execute_cmd')
    def test_is_installed(self, mock_execute):
        proc_mock = mock.Mock()
        proc_mock.returncode = 0
        mock_execute.return_value = proc_mock

        result = self._hana.is_installed()

        mock_execute.assert_called_once_with('HDB info', 'prdadm', 'pass')

        self.assertTrue(result)

    @mock.patch('shaptools.shell.execute_cmd')
    def test_is_installed_error(self, mock_execute):
        proc_mock = mock.Mock()
        proc_mock.returncode = 1
        mock_execute.return_value = proc_mock

        result = self._hana.is_installed()

        mock_execute.assert_called_once_with('HDB info', 'prdadm', 'pass')

        self.assertFalse(result)

    @mock.patch('shaptools.shell.execute_cmd')
    @mock.patch('logging.Logger.error')
    def test_is_installed_not_found(self, logger, mock_execute):
        proc_mock = mock.Mock()
        proc_mock.returncode = 1
        error = EnvironmentError('test exception')
        mock_execute.side_effect = error

        result = self._hana.is_installed()

        mock_execute.assert_called_once_with('HDB info', 'prdadm', 'pass')

        self.assertFalse(result)
        logger.assert_called_once_with(error)

    def test_update_conf_file(self):
        pwd = os.path.dirname(os.path.abspath(__file__))
        shutil.copyfile(pwd+'/support/original.conf', '/tmp/copy.conf')
        conf_file = hana.HanaInstance.update_conf_file(
            '/tmp/copy.conf', sid='PRD',
            password='Qwerty1234', system_user_password='Qwerty1234')
        self.assertTrue(filecmp.cmp(pwd+'/support/modified.conf', conf_file))

        shutil.copyfile(pwd+'/support/original.conf', '/tmp/copy.conf')
        conf_file = hana.HanaInstance.update_conf_file(
            '/tmp/copy.conf',
            **{'sid': 'PRD', 'password': 'Qwerty1234', 'system_user_password': 'Qwerty1234'})
        self.assertTrue(filecmp.cmp(pwd+'/support/modified.conf', conf_file))

    @mock.patch('shaptools.shell.execute_cmd')
    def test_create_conf_file(self, mock_execute):
        proc_mock = mock.Mock()
        proc_mock.returncode = 0
        mock_execute.return_value = proc_mock

        conf_file = hana.HanaInstance.create_conf_file(
            'software_path', 'conf_file.conf', 'root', 'pass')

        mock_execute.assert_called_once_with(
            'software_path/DATA_UNITS/HDB_LCM_LINUX_X86_64/hdblcm '
            '--action=install --dump_configfile_template={conf_file}'.format(
                conf_file='conf_file.conf'), 'root', 'pass')
        self.assertEqual('conf_file.conf', conf_file)

    @mock.patch('shaptools.shell.execute_cmd')
    def test_create_conf_file_error(self, mock_execute):
        proc_mock = mock.Mock()
        proc_mock.returncode = 1
        mock_execute.return_value = proc_mock

        with self.assertRaises(hana.HanaError) as err:
            hana.HanaInstance.create_conf_file(
                'software_path', 'conf_file.conf', 'root', 'pass')

        mock_execute.assert_called_once_with(
            'software_path/DATA_UNITS/HDB_LCM_LINUX_X86_64/hdblcm '
            '--action=install --dump_configfile_template={conf_file}'.format(
                conf_file='conf_file.conf'), 'root', 'pass')

        self.assertTrue(
            'SAP HANA configuration file creation failed' in str(err.exception))

    @mock.patch('shaptools.shell.execute_cmd')
    def test_install(self, mock_execute):
        proc_mock = mock.Mock()
        proc_mock.returncode = 0
        mock_execute.return_value = proc_mock

        hana.HanaInstance.install(
            'software_path', 'conf_file.conf', 'root', 'pass')

        mock_execute.assert_called_once_with(
            'software_path/DATA_UNITS/HDB_LCM_LINUX_X86_64/hdblcm '
            '-b --configfile={conf_file}'.format(
                conf_file='conf_file.conf'), 'root', 'pass')

    @mock.patch('shaptools.shell.execute_cmd')
    def test_install_error(self, mock_execute):
        proc_mock = mock.Mock()
        proc_mock.returncode = 1
        mock_execute.return_value = proc_mock

        with self.assertRaises(hana.HanaError) as err:
            hana.HanaInstance.install(
                'software_path', 'conf_file.conf', 'root', 'pass')

        mock_execute.assert_called_once_with(
            'software_path/DATA_UNITS/HDB_LCM_LINUX_X86_64/hdblcm '
            '-b --configfile={conf_file}'.format(
                conf_file='conf_file.conf'), 'root', 'pass')

        self.assertTrue(
            'SAP HANA installation failed' in str(err.exception))

    @mock.patch('shaptools.shell.execute_cmd')
    def test_uninstall(self, mock_execute):
        proc_mock = mock.Mock()
        proc_mock.returncode = 0
        mock_execute.return_value = proc_mock

        self._hana.uninstall('root', 'pass')

        mock_execute.assert_called_once_with(
            '/hana/shared/PRD/hdblcm/hdblcm --uninstall -b', 'root', 'pass')

    @mock.patch('shaptools.shell.execute_cmd')
    def test_uninstall_error(self, mock_execute):
        proc_mock = mock.Mock()
        proc_mock.returncode = 1
        mock_execute.return_value = proc_mock

        with self.assertRaises(hana.HanaError) as err:
            self._hana.uninstall('root', 'pass', 'path')

        mock_execute.assert_called_once_with(
            'path/PRD/hdblcm/hdblcm --uninstall -b', 'root', 'pass')

        self.assertTrue(
            'SAP HANA uninstallation failed' in str(err.exception))

    @mock.patch('shaptools.shell.execute_cmd')
    def test_is_running(self, mock_execute):
        proc_mock = mock.Mock()
        proc_mock.returncode = 0
        mock_execute.return_value = proc_mock

        result = self._hana.is_running()

        mock_execute.assert_called_once_with('pidof hdb.sapPRD_HDB00')
        self.assertTrue(result)

    @mock.patch('subprocess.Popen')
    def test_get_version(self, mock_popen):
        out = (b"Output text\n"
               b"  version:  1.2.3.4.5\n"
               b"line2")

        mock_popen_inst = mock.Mock()
        mock_popen_inst.returncode = 0
        mock_popen_inst.communicate.return_value = (out, b'err')
        mock_popen.return_value = mock_popen_inst

        version = self._hana.get_version()

        self.assertEqual('1.2.3', version)

    @mock.patch('subprocess.Popen')
    def test_get_version_error(self, mock_popen):
        out = (b"Output text\n"
               b"  versionn:  1.2.3.4.5\n"
               b"line2")

        mock_popen_inst = mock.Mock()
        mock_popen_inst.returncode = 0
        mock_popen_inst.communicate.return_value = (out, b'err')
        mock_popen.return_value = mock_popen_inst

        with self.assertRaises(hana.HanaError) as err:
            self._hana.get_version()

        self.assertTrue(
            'Version pattern not found in command output' in str(err.exception))

    def test_start(self):
        mock_command = mock.Mock()
        self._hana._run_hana_command = mock_command
        self._hana.start()
        mock_command.assert_called_once_with('HDB start')

    def test_stop(self):
        mock_command = mock.Mock()
        self._hana._run_hana_command = mock_command
        self._hana.stop()
        mock_command.assert_called_once_with('HDB stop')

    def test_get_sr_state_primary(self):

        result_mock = mock.Mock()
        result_mock.find_pattern.return_value = True

        mock_command = mock.Mock()
        mock_command.return_value = result_mock
        self._hana._run_hana_command = mock_command

        state = self._hana.get_sr_state()

        result_mock.find_pattern.assert_called_once_with('.*mode: primary.*')
        mock_command.assert_called_once_with('hdbnsutil -sr_state')

        self.assertEqual(hana.SrStates.PRIMARY, state)

    def test_get_sr_state_secondary(self):
        result_mock = mock.Mock()
        result_mock.find_pattern.side_effect = [False, True]

        mock_command = mock.Mock()
        mock_command.return_value = result_mock
        self._hana._run_hana_command = mock_command

        state = self._hana.get_sr_state()

        mock_command.assert_called_once_with('hdbnsutil -sr_state')
        result_mock.find_pattern.assert_has_calls([
            mock.call('.*mode: primary.*'),
            mock.call('.*mode: (sync|syncmem|async)')
        ])
        self.assertEqual(hana.SrStates.SECONDARY, state)

    def test_get_sr_state_disabled(self):
        result_mock = mock.Mock()
        result_mock.find_pattern.side_effect = [False, False]

        mock_command = mock.Mock()
        mock_command.return_value = result_mock
        self._hana._run_hana_command = mock_command

        state = self._hana.get_sr_state()

        mock_command.assert_called_once_with('hdbnsutil -sr_state')
        result_mock.find_pattern.assert_has_calls([
            mock.call('.*mode: primary.*'),
            mock.call('.*mode: (sync|syncmem|async)')
        ])
        self.assertEqual(hana.SrStates.DISABLED, state)

    def test_enable(self):
        mock_command = mock.Mock()
        self._hana._run_hana_command = mock_command
        self._hana.sr_enable_primary('test')
        mock_command.assert_called_once_with(
            'hdbnsutil -sr_enable --name={}'.format('test'))

    def test_disable(self):
        mock_command = mock.Mock()
        self._hana._run_hana_command = mock_command
        self._hana.sr_disable_primary()
        mock_command.assert_called_once_with('hdbnsutil -sr_disable')

    def test_register(self):
        mock_command = mock.Mock()
        self._hana._run_hana_command = mock_command
        self._hana.sr_register_secondary('test', 'host', '00', 'sync', 'ops')
        mock_command.assert_called_once_with(
            'hdbnsutil -sr_register --name={} --remoteHost={} '\
            '--remoteInstance={} --replicationMode={} --operationMode={}'.format(
            'test', 'host', '00', 'sync', 'ops'))

    def test_unregister(self):
        mock_command = mock.Mock()
        self._hana._run_hana_command = mock_command
        self._hana.sr_unregister_secondary('test')
        mock_command.assert_called_once_with(
            'hdbnsutil -sr_unregister --name={}'.format('test'))

    def test_check_user_key(self):
        mock_command = mock.Mock()
        self._hana._run_hana_command = mock_command

        result = self._hana.check_user_key('key')
        mock_command.assert_called_once_with(
            'hdbuserstore list {}'.format('key'))
        self.assertTrue(result)

    def test_check_user_key_error(self):
        mock_command = mock.Mock()
        mock_command.side_effect = hana.HanaError('test error')
        self._hana._run_hana_command = mock_command

        result = self._hana.check_user_key('key')
        mock_command.assert_called_once_with(
            'hdbuserstore list {}'.format('key'))
        self.assertFalse(result)

    def test_create_user_key(self):
        mock_command = mock.Mock()
        self._hana._run_hana_command = mock_command

        self._hana.create_user_key('key', 'envi', 'user', 'pass')
        mock_command.assert_called_once_with(
            'hdbuserstore set {key} {env}{db} {user} {passwd}'.format(
            key='key', env='envi', db=None,
            user='user', passwd='pass'))

    def test_create_user_key_db(self):
        mock_command = mock.Mock()
        self._hana._run_hana_command = mock_command

        self._hana.create_user_key('key', 'envi', 'user', 'pass', 'db')
        mock_command.assert_called_once_with(
            'hdbuserstore set {key} {env}{db} {user} {passwd}'.format(
            key='key', env='envi', db='@db',
            user='user', passwd='pass'))

    def test_create_backup(self):
        mock_command = mock.Mock()
        self._hana._run_hana_command = mock_command

        self._hana.create_backup('key', 'pass', 'db', 'backup')
        mock_command.assert_called_once_with(
            'hdbsql -U {} -d {} -p {} '\
            '\\"BACKUP DATA FOR FULL SYSTEM USING FILE (\'{}\')\\"'.format(
            'key', 'db', 'pass', 'backup'))

    def test_sr_cleanup(self):
        mock_command = mock.Mock()
        self._hana._run_hana_command = mock_command

        self._hana.sr_cleanup()
        mock_command.assert_called_once_with('hdbnsutil -sr_cleanup')

    def test_sr_cleanup_force(self):
        mock_command = mock.Mock()
        self._hana._run_hana_command = mock_command

        self._hana.sr_cleanup(force=True)
        mock_command.assert_called_once_with('hdbnsutil -sr_cleanup --force')
