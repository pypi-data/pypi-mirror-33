from collections.abc import MutableSet

from qborg.entities.repository import Repository


class RepositorySet(MutableSet):
    def __init__(self, iterable=[]):
        self._repositories = set(iterable)

    def __eq__(self, other):
        if type(self) == type(other):
            return self._repositories == other._repositories

        if type(other) == set:
            return self._repositories == other

        if type(other) == list:
            return self._repositories == set(other)

        return NotImplemented

    def __len__(self):
        return len(self._repositories)

    def __getitem__(self, key):
        if not isinstance(key, str):
            raise TypeError('key must be a str')

        item = self._get_by_name(key)
        if item is not None:
            return item

        raise KeyError('No repository named %s' % key)

    def __delitem__(self, key):
        if not isinstance(key, str):
            raise TypeError('key must be a str')

        item = self._get_by_name(key)
        if item is not None:
            self._repositories.remove(item)

        raise KeyError('No repository named %s' % key)

    def _get_by_name(self, name):
        try:
            return next(repo for repo in self._repositories if repo.name == name)
        except StopIteration:
            return None

    def _contains_name(self, name):
        return (self._get_by_name(name) is not None)

    def __contains__(self, item):
        return item in self._repositories

    def __iter__(self):
        return iter(self._repositories)

    def add(self, item):
        if not isinstance(item, Repository):
            raise TypeError('item must be a Repository')

        repo_name = item.name
        if self._contains_name(repo_name):
            raise ValueError('There is already a repository with name %s in the set' % repo_name)

        self._repositories.add(item)

    def discard(self, item):
        self._repositories.discard(item)

    def dump(self):
        obj = dict()

        for repo in self._repositories:
            repo_name, repo_params = repo.dump()
            obj[repo_name] = repo_params

        return obj

    @classmethod
    def load(cls, obj):
        if not isinstance(obj, dict):
            raise ValueError('Serialized repositories are not a dict')

        thawed = RepositorySet()

        for repo_name, repo_params in obj.items():
            thawed.add(Repository.load(repo_name, repo_params))

        return thawed


class Config():
    def __init__(self):
        self._repositories = RepositorySet()

    def __eq__(self, other):
        if type(self) == type(other):
            return vars(self) == vars(other)

        return NotImplemented

    @property
    def repositories(self):
        return self._repositories

    def dump(self):
        return {
            'repositories': self._repositories.dump()
        }

    @classmethod
    def load(cls, obj):
        thawed = Config()

        try:
            repositories = obj['repositories']
        except KeyError:
            raise ValueError('Corrupted config. No repositories key')

        thawed._repositories = RepositorySet.load(repositories)

        return thawed
