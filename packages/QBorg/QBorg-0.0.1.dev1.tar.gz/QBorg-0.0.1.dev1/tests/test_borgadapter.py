import pytest
import subprocess

from unittest import TestCase
from unittest.mock import patch
from distutils.version import StrictVersion

from qborg.adapters.backup.borg import BorgAdapter


class BorgAdapterTest(TestCase):

    @patch('shutil.which', autospec=True)
    def test_find_executable(self, which_mock):
        _fake_borg_path = '/usr/fake/bin/borg'
        which_mock.return_value = _fake_borg_path

        found_borg = BorgAdapter._find_borg_executable('borg')

        assert found_borg == _fake_borg_path

    @patch('shutil.which', autospec=True)
    def test_find_executable_nonexist(self, which_mock):
        with pytest.raises(ValueError):
            BorgAdapter._find_borg_executable('/non/exist/borg')

        assert not which_mock.called

    def test_constructor_find_borg(self):
        with pytest.raises(ValueError):
            BorgAdapter(borg_bin='/non/exist/borg')

        with patch('shutil.which') as which_mock:
            _fake_borg_path = '/usr/fake/bin/borg'
            which_mock.return_value = _fake_borg_path
            adapter = BorgAdapter()
            assert adapter.borg_bin == _fake_borg_path

    def test_get_borg_version(self):
        with patch('shutil.which') as which_mock:
            which_mock.return_value = '/usr/fake/bin/borg'
            adapter = BorgAdapter()

        with pytest.raises(NotImplementedError):
            adapter.get_borg_version()

    def test_is_min_version(self):
        with patch('shutil.which') as which_mock:
            which_mock.return_value = '/usr/fake/bin/borg'
            adapter = BorgAdapter()

        with patch.object(adapter, 'get_borg_version') as version_mock:
            version_mock.return_value = StrictVersion('1.1')

            assert adapter.is_min_version('1.0')
            assert not adapter.is_min_version('1.2')
            assert adapter.is_min_version('1.1')  # edge case

    @patch('subprocess.check_output', autospec=True)
    def test_get_detected_version_nonexist(self, subproc_mock):
        subproc_mock.side_effect = FileNotFoundError()

        version = BorgAdapter.get_detected_version('/non/exist/borg')
        assert version is None

    @patch('subprocess.check_output', autospec=True)
    def test_get_detected_version(self, subproc_mock):
        subproc_mock.return_value = b'borg 1.1.5\n'

        version = BorgAdapter.get_detected_version('/non/exist/borg')

        assert version == StrictVersion('1.1.5')

        subproc_mock.assert_called_once_with(['/non/exist/borg', '--version'], stderr=subprocess.STDOUT)
