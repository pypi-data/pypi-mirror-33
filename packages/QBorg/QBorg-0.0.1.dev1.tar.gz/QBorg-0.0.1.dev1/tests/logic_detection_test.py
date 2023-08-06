from unittest import TestCase
from unittest.mock import patch
from distutils.version import StrictVersion
from qborg.logic.detection import ToolDetection


class ToolDetectionTest(TestCase):

    def setUp(self):
        self.borg_bin = '/usr/fake/bin/borg'
        ToolDetection._borg_version = None

    @patch('subprocess.check_output', autospec=True)
    def test_get_borg_version(self, subproc_mock):
        _test_values = {
            b'borg 1.1.5\n': StrictVersion('1.1.5'),
            b'borg 1.1.0\n': StrictVersion('1.1.0'),
            b'borg 1.1.0rc4\n': StrictVersion('1.1.0'),
            b'borg 1.0.12\n': StrictVersion('1.0.12'),
            b'borg 0.30.1\n': StrictVersion('0.30.1'),
        }

        for stdout_str, correct_version in _test_values.items():
            subproc_mock.return_value = stdout_str

            ToolDetection._borg_version = None  # reset cached version
            version = ToolDetection.get_borg_version(self.borg_bin)

            assert version is not None  # a version is detected
            assert version == correct_version  # ... and it is correct

    @patch('subprocess.check_output', autospec=True)
    def test_get_borg_version_returns_none_if_no_borg_found(self, subproc_mock):
        subproc_mock.side_effect = FileNotFoundError()

        version = ToolDetection.get_borg_version('/non/exist/borg')
        assert version is None

    def test_get_borg_version_is_cached(self):
        with patch('subprocess.check_output', autospec=True) as subproc_mock:
            subproc_mock.return_value = b'borg 1.1.5\n'

            version = ToolDetection.get_borg_version(self.borg_bin)
            assert version is not None
            assert version == StrictVersion('1.1.5')

        # Version is cached and not requested again after it worked the first time
        with patch('subprocess.check_output') as subproc_mock:
            subproc_mock.side_effect = FileNotFoundError()
            version2 = ToolDetection.get_borg_version('/non/exist/borg')

            assert not subproc_mock.called
            assert version is not None
            assert version == version2
