import os
import tempfile
import unittest

from qborg.entities.location import Location
from qborg.logic.factories import BackingStoreAdapterFactory


class TestLocation(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(tempfile.gettempdir(), 'qborg', 'TestLocation')
        self.backingstore = BackingStoreAdapterFactory.adapter_for_url('file://' + self.path)
        self.location = Location(self.backingstore, self.path)

        self.valid_dump = {
            'backingstore': self.backingstore.protocol,
            'path': self.path
        }

    def test_eq(self):
        self.assertTrue(self.location.__eq__(Location(self.backingstore, self.path)))

    def test_dump(self):
        self.assertEqual(self.location.dump(), self.valid_dump)

    def test_load(self):
        self.assertTrue(self.location.__eq__(Location.load(self.valid_dump)))
