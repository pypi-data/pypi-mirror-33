import os
import tempfile

from unittest import TestCase

from qborg.adapters.backingstore.file import FileBackingStoreAdapter


class FileBackingStoreAdapterTest(TestCase):

    def setUp(self):
        self.adapter = FileBackingStoreAdapter(mountpoint='/')

    def test_posix_path_generation(self):
        paths = {
            '/non_exist': '/non_exist',
            'non_exist': '/non_exist',
            '/tmp/non_exist': '/tmp/non_exist',
            'tmp/non_exist': '/tmp/non_exist',
            '/non_exist/': '/non_exist',
        }

        for path, posix_path in paths.items():
            assert posix_path == self.adapter.posix_path(path)

    def test_symlink_resolution(self):
        # Create a tempfile
        with tempfile.NamedTemporaryFile(delete=True) as tmpfile:
            try:
                # ... and a symlink to it
                symlink = tempfile.mktemp()
                os.symlink(tmpfile.name, symlink)  # will raise on Windows < 6.0

                # Assert that the posix_path function does not resolve the symlink
                assert symlink == self.adapter.posix_path(symlink)
                assert tmpfile.name != self.adapter.posix_path(symlink)
            finally:
                # Delete symlink
                if os.path.exists(symlink):
                    os.unlink(symlink)

    def test_borg_url_generation(self):
        paths = ['/non_exist', 'non_exist', '/tmp/non_exist', 'tmp/non_exist']

        for path in paths:
            assert self.adapter.borg_url(path) == ('file://' + self.adapter.posix_path(path))

    def test_exists(self):
        paths = {
            '/dev/null': os.path.exists('/dev/null'),
            'non_exist': os.path.exists('/non_exist'),
            '/tmp/': os.path.exists('/tmp')
        }

        for path, exists in paths.items():
            assert exists == self.adapter.exists(path)
