import qborg

from unittest import TestCase
from unittest.mock import patch

from qborg.logic.factories import BackupAdapterFactory, BackingStoreAdapterFactory


class BackupAdapterFactoryTest(TestCase):

    @patch('qborg.adapters.backup.borg.BorgAdapter._find_borg_executable')
    def test_get_adapter(self, find_borg_mock):
        find_borg_mock.return_value = '/usr/fake/bin/borg'
        adapter = BackupAdapterFactory.get_adapter()
        expected_class = qborg.adapters.backup.borg.borg11adapter.Borg11Adapter  # FIXME
        assert isinstance(adapter, expected_class)


class BackingStoreAdapterFactoryTest(TestCase):

    def test_adapter_for_protocol(self):
        adapter_mappings = {
            'file': qborg.adapters.backingstore.file.FileBackingStoreAdapter
        }

        for proto, clazz in adapter_mappings.items():
            adapter = BackingStoreAdapterFactory.adapter_for_protocol(proto)
            assert isinstance(adapter, clazz)

    def test_adapter_for_url(self):
        adapter_mappings = {
            'file:///tmp': qborg.adapters.backingstore.file.FileBackingStoreAdapter
        }

        for url, clazz in adapter_mappings.items():
            adapter = BackingStoreAdapterFactory.adapter_for_url(url)
            assert isinstance(adapter, clazz)
