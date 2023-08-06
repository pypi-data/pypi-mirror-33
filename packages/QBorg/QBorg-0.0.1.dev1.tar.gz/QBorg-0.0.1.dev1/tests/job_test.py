import unittest

from qborg.entities.job import Job


class TestJob(unittest.TestCase):
    def setUp(self):
        self.precommand = 'a_script.sh'
        self.postcommand = 'another_script.sh'
        self.include = '/home/user1/'
        self.exclude = '/home/user1/borg_repos'

        self.job = Job('TestJob')

    def test_command(self):
        job = Job('TestJob')

        precommand1 = self.precommand
        precommand2 = precommand1 + 'h'
        precommand3 = precommand2 + 'h'

        self.job.precommands.append(precommand1)
        job.precommands.append(precommand1)

        self.job.precommands.prepend(precommand2)
        job.precommands.prepend(precommand2)

        self.job.precommands.insert(1, precommand3)
        job.precommands.insert(1, precommand3)

        assert self.job.precommands == [precommand2, precommand3, precommand1]
        assert self.job.precommands.__eq__(job.precommands)

    def test_precommand(self):
        self.job.precommands.append(self.precommand)
        assert self.job.precommands == [self.precommand]

        del self.job.precommands[0]
        assert self.job.precommands == []

        with self.assertRaises(IndexError):
            del self.job.precommands[0]

    def test_postcommand(self):
        self.job.postcommands.append(self.postcommand)
        assert self.job.postcommands == [self.postcommand]

        del self.job.postcommands[0]
        assert self.job.postcommands == []

        with self.assertRaises(IndexError):
            del self.job.postcommands[0]

    def test_includes(self):
        self.job.includes.append(self.include)
        assert self.job.includes == [self.include]

        del self.job.includes[0]
        assert self.job.includes == []

        with self.assertRaises(IndexError):
            del self.job.includes[0]

    def test_excludes(self):
        self.job.excludes.append(self.exclude)
        assert self.job.excludes == [self.exclude]

        del self.job.excludes[0]
        assert self.job.excludes == []

        with self.assertRaises(IndexError):
            del self.job.excludes[0]

    def _get_test_job(self, name='TestJob'):
        job = Job(name)
        job.precommands.append(self.precommand)
        job.postcommands.append(self.postcommand)
        job.includes.append(self.include)
        job.excludes.append(self.exclude)

        return job

    def test_dump(self):
        job_name = 'TestJob'
        job = self._get_test_job(job_name)

        assert job.dump() == (job_name, {
            'precommands': [self.precommand],
            'postcommands': [self.postcommand],
            'includes': [self.include],
            'excludes': [self.exclude]
        })

    def test_load(self):
        job_name = 'TestJob'
        job = self._get_test_job(job_name)

        job_thawed = Job.load(job_name, {
            'precommands': [self.precommand],
            'postcommands': [self.postcommand],
            'includes': [self.include],
            'excludes': [self.exclude]
        })

        assert job == job_thawed
