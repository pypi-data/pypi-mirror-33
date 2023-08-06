from collections.abc import MutableSequence


class CommandList(MutableSequence):
    def __init__(self, iterable=[]):
        self._commands = list(iterable)

    def __eq__(self, other):
        if type(self) == type(other):
            return self._commands == other._commands

        if isinstance(other, list):
            return self._commands == other

        return NotImplemented

    def __len__(self):
        return len(self._commands)

    def __getitem__(self, i):
        return self._commands[i]

    def __setitem__(self, i, value):
        if not isinstance(value, str):
            raise ValueError('value must be a str')

        self._commands[i] = value

    def __delitem__(self, i):
        del self._commands[i]

    def insert(self, i, value):
        self._commands.insert(i, value)

    def prepend(self, value):
        self._commands.insert(0, value)

    def append(self, value):
        self._commands.insert(len(self._commands), value)

    def dump(self):
        return self._commands

    @classmethod
    def load(cls, obj):
        if not isinstance(obj, list):
            raise TypeError('obj is not a list')

        return CommandList(obj)


class Job:
    def __init__(self, name):
        self._name = name
        self._precommands = CommandList()
        self._postcommands = CommandList()
        self._includes = list()
        self._excludes = list()

    def __eq__(self, other):
        if type(self) == type(other):
            return vars(self) == vars(other)

        return NotImplemented

    def __hash__(self):
        return hash((self._name,))

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def precommands(self):
        return self._precommands

    @property
    def postcommands(self):
        return self._postcommands

    @property
    def includes(self):
        return self._includes

    @property
    def excludes(self):
        return self._excludes

    def dump(self):
        return self.name, {
            'precommands': self._precommands.dump(),
            'postcommands': self._postcommands.dump(),
            'excludes': self._excludes,
            'includes': self._includes
        }

    @classmethod
    def load(cls, name, obj):
        if not isinstance(obj, dict):
            raise TypeError('obj is not a dict')

        thawed = Job(name)

        if 'precommands' in obj:
            thawed._precommands = CommandList.load(obj['precommands'])

        if 'postcommands' in obj:
            thawed._postcommands = CommandList.load(obj['postcommands'])

        if 'includes' in obj:
            thawed._includes = obj['includes']

        if 'excludes' in obj:
            thawed._excludes = obj['excludes']

        return thawed
