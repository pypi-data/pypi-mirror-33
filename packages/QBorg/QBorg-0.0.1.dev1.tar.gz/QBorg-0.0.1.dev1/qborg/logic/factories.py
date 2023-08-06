class BackupAdapterFactory():
    """
    Creates instances of BorgAdapters
    """

    @classmethod
    def get_adapter(cls):
        from qborg.adapters.backup.borg.borg11adapter import Borg11Adapter
        return Borg11Adapter()


class BackingStoreAdapterFactory():
    """
    Creates instances of BackingStoreAdapters
    """

    import qborg.adapters.backingstore.file

    _protocol_adapters = {
        'file': qborg.adapters.backingstore.file.FileBackingStoreAdapter
    }

    @classmethod
    def adapter_for_protocol(cls, protocol):
        try:
            cls = cls._protocol_adapters[protocol.lower()]
            return cls()
        except Exception:
            return None

    @classmethod
    def adapter_for_url(cls, url):
        # TODO: Extract protocol from URL
        protocol = 'file'
        return cls.adapter_for_protocol(protocol)
