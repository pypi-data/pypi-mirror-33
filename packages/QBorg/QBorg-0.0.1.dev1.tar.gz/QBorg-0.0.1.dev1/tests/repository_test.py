import enum
import unittest

from unittest.mock import patch

from qborg.adapters.backingstore.file import FileBackingStoreAdapter
from qborg.adapters.backup.borg import BorgAdapter
from qborg.entities.repository import Job
from qborg.entities.location import Location
from qborg.entities.repository import JobSet
from qborg.entities.repository import Repository


class BorgMockEncryptionMode(enum.Enum):
    NONE = 'none'


class BorgMockAdapter(BorgAdapter):
    supported_encryption_modes = BorgMockEncryptionMode


class RepositoryTest(unittest.TestCase):
    def setUp(self):
        self._precommand = 'a_script.sh'
        self._postcommand = 'another_script.sh'
        self._include = '/home/user1/'
        self._exclude = '/home/user1/borg_repos'
        self._prune_weekly = 5
        self._prune_monthly = 1

        self._location = Location(FileBackingStoreAdapter(), '/tmp/qborg_test_set_location_dir')
        self._encryption_mode = BorgMockEncryptionMode.NONE

        self._job = Job('RepoTestJob')
        self._job.precommands.append(self._precommand)
        self._job.postcommands.append(self._postcommand)
        self._job.includes.append(self._include)
        self._job.excludes.append(self._exclude)

    def test_job(self):
        repository = Repository('JobTestRepo', self._location, self._encryption_mode)

        # Set
        repository.jobs.add(self._job)
        assert repository.jobs == set([self._job])

        with self.assertRaises(ValueError):
            repository.jobs.add(self._job)
        assert len(repository.jobs) == 1

        # Get
        assert repository.jobs[self._job.name] == self._job
        assert repository.jobs['non existing job'] is None

        # Remove
        assert self._job in repository.jobs
        repository.jobs.discard(self._job)
        assert self._job not in repository.jobs

        with self.assertRaises(KeyError):
            # This should fail because the job has already been removed
            repository.jobs.remove(self._job)

    def test_prune(self):
        _values = {
            'keep_secondly': 0,
            'keep_minutely': 0,
            'keep_hourly': 0,
            'keep_daily': 15,
            'keep_weekly': 3,
            'keep_monthly': 1,
            'keep_yearly': 2,
            'keep_last': 5,
            'keep_within': '3H',
        }

        repository = Repository('PruneTestRepo', self._location, self._encryption_mode)

        for k, v in _values.items():
            repository.prune[k] = v
            assert v == repository.prune[k]

    def test_dump(self):
        repo_name = 'DumpTestRepo'
        repository = Repository(repo_name, self._location, self._encryption_mode)
        repository.prune['keep_weekly'] = self._prune_weekly
        repository.prune['keep_monthly'] = self._prune_monthly

        repository.jobs.add(self._job)

        assert repository.dump() == (repo_name, {
            'location': self._location.dump(),
            'encryption_mode': 'none',
            'jobs': {
                self._job.name: {
                    'precommands': [self._precommand],
                    'postcommands': [self._postcommand],
                    'includes': [self._include],
                    'excludes': [self._exclude]
                }
            },
            'prune': {
                'keep_weekly': self._prune_weekly,
                'keep_monthly': self._prune_monthly
            }
        })

    def test_load(self):
        repo_name = 'LoadTestRepo'
        repository = Repository(repo_name, self._location, self._encryption_mode)
        repository.prune['keep_daily'] = 30
        repository.prune['keep_monthly'] = 6
        repository.jobs.add(self._job)

        with patch('qborg.logic.factories.BackupAdapterFactory.get_adapter') as factory_mock:
            factory_mock.return_value = BorgMockAdapter
            repository_thawed = Repository.load(repo_name, {
                'location': self._location.dump(),
                'encryption_mode': 'none',
                'jobs': {
                    self._job.name: self._job.dump()[1]
                },
                'prune': {
                    'keep_daily': 30,
                    'keep_monthly': 6,
                }
            })

        self.assertTrue(repository.__eq__(repository_thawed))

        with patch('qborg.logic.factories.BackupAdapterFactory.get_adapter') as factory_mock:
            factory_mock.return_value = BorgMockAdapter
            # Sould raise an error when an invalid prune key is encountered
            with self.assertRaises(KeyError):
                Repository.load(repo_name, {
                    'location': self._location.dump(),
                    'encryption_mode': 'none',
                    'prune': {
                        'invalid_key': -1
                    }
                })


class TestJobSet(unittest.TestCase):
    def setUp(self):
        self._precommand = 'a_script.sh'
        self._postcommand = 'another_script.sh'
        self._include = '/home/user1/'
        self._exclude = '/home/user1/borg_repos'

        self._job = Job('RepoTestJob')
        self._job.precommands.append(self._precommand)
        self._job.postcommands.append(self._postcommand)
        self._job.includes.append(self._include)
        self._job.excludes.append(self._exclude)

        self._job_set = JobSet()

    def test_eq(self):
        job = Job('RepoTestJob')
        job.precommands.append(self._precommand)
        job.postcommands.append(self._postcommand)
        job.includes.append(self._include)
        job.excludes.append(self._exclude)

        job_set = JobSet()
        job_set.add(job)

        self._job_set.add(self._job)
        self.assertTrue(self._job_set.__eq__(job_set))

    def test_job_set(self):
        self._job_set.add(self._job)

        with self.assertRaises(ValueError):
            self._job_set.add(self._job)
