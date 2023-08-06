from collections.abc import MutableSet

from qborg.entities.job import Job
from qborg.entities.location import Location


class JobSet(MutableSet):
    def __init__(self, iterable=[]):
        self._jobs = set(iterable)

    def __eq__(self, other):
        if type(self) == type(other):
            return self._jobs == other._jobs

        if type(other) == set:
            return self._jobs == other

        return NotImplemented

    def __len__(self):
        return len(self._jobs)

    def __getitem__(self, name):
        for job in self._jobs:
            if job.name == name:
                return job

        return None

    def _contains_name(self, name):
        try:
            next(job for job in self._jobs if job.name == name)
            return True
        except StopIteration:
            return False

    def __contains__(self, item):
        return item in self._jobs

    def __iter__(self):
        return iter(self._jobs)

    def add(self, item):
        if not isinstance(item, Job):
            raise ValueError('item is not a Job')

        job_name = item.name
        if self._contains_name(job_name):
            raise ValueError('There is already a job with name %s in the set' % job_name)

        self._jobs.add(item)

    def discard(self, item):
        self._jobs.discard(item)

    def dump(self):
        obj = dict()
        for job in self._jobs:
            if not hasattr(job, 'name'):
                raise ValueError('job has no name. break.')
            name, params = job.dump()
            obj[name] = params

        return obj

    @classmethod
    def load(cls, obj):
        if not isinstance(obj, dict):
            raise ValueError('obj must be a serialized jobs dict')

        jobs = JobSet()

        for k, v in obj.items():
            jobs.add(Job.load(k, v))

        return jobs


class Repository():
    _valid_prune_keys = [
        'keep_within', 'keep_last', 'keep_secondly', 'keep_minutely',
        'keep_hourly', 'keep_daily', 'keep_weekly', 'keep_monthly',
        'keep_yearly'
    ]

    def __init__(self, name, location, encryption_mode):
        self._name = name
        self._location = location
        self._encryption_mode = encryption_mode
        self._jobs = JobSet()
        self._prune = dict()

    def __eq__(self, other):
        if type(self) == type(other):
            return vars(self) == vars(other)

        return NotImplemented

    def __hash__(self):
        return hash((self._location, self._encryption_mode))

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def location(self):
        return self._location

    @property
    def encryption_mode(self):
        return self._encryption_mode

    @property
    def password(self):
        try:
            return self._password
        except AttributeError:
            return None

    @password.setter
    def password(self, value):
        self._password = value

    @property
    def jobs(self):
        return self._jobs

    @property
    def prune(self):
        # TODO: Check keys in setter
        return self._prune

    def dump(self):
        obj = {
            'jobs': self._jobs.dump(),
            'location': self._location.dump(),
            'encryption_mode': self._encryption_mode.value
        }

        if 0 < len(self._prune):
            obj['prune'] = self._prune

        return self._name, obj

    @classmethod
    def load(cls, name, obj):
        if not isinstance(obj, dict):
            raise TypeError('obj is not a dict')

        from qborg.logic.factories import BackupAdapterFactory

        try:
            location_dict = obj['location']
            encryption_mode_str = obj['encryption_mode']

            # HACK: The load() method should not need to create an adapter to
            # get the supported encryption modes. We need a better way to track
            # the used Borg version in the serialized form.
            backup_adapter = BackupAdapterFactory.get_adapter()
            encryption_modes = backup_adapter.supported_encryption_modes
            encryption_mode = encryption_modes(encryption_mode_str)
        except KeyError as e:
            raise ValueError('Corrupted repository %s' % name,
                             '%s not specified' % e.args[0])

        location = Location.load(location_dict)
        thawed = Repository(name, location, encryption_mode)

        if 'jobs' in obj:
            thawed._jobs = JobSet.load(obj['jobs'])

        if 'prune' in obj:
            for k, v in obj['prune'].items():
                if k in cls._valid_prune_keys:
                    thawed._prune[k] = v
                else:
                    raise KeyError('%s is not a valid prune option' % k)

        return thawed

    # used for the table of its backups
    def table_row_header(self):
        return ['Name', 'Time']
