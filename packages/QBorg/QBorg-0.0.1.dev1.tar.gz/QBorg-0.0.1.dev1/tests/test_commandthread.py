import shutil

from unittest import TestCase
from unittest.mock import Mock, patch

from qborg.util.commandthread import CommandThread, ICommandDelegate


class LoggerDelegate(ICommandDelegate):
    stdout_line_call_count = 0
    stderr_line_call_count = 0
    stdout_buffer = []
    stderr_buffer = []
    rc = None

    def stdout_line(self, line):
        self.stdout_line_call_count += 1
        self.stdout_buffer.append(line)

    def stderr_line(self, line):
        self.stderr_line_call_count += 1
        self.stderr_buffer.append(line)

    def process_terminated(self, rc):
        self.rc = rc


class CommandThreadTest(TestCase):
    @patch('subprocess.Popen', autospec=True)
    def test_popen(self, Popen_mock):
        mock_rv = Mock()
        mock_rv.communicate.return_value = ["", ""]
        Popen_mock.return_value = mock_rv

        command = ['/bin/true']
        thd = CommandThread(command, delegate=None)
        thd.start()
        thd.join()

        assert Popen_mock.called
        Popen_mock.assert_called_once_with(command, bufsize=1, stderr=-1, cwd=None,
                                           stdin=-3, stdout=-1, universal_newlines=True)

    @patch('subprocess.Popen', autospec=True)
    def test_popen_with_cwd(self, Popen_mock):
        Popen_mock.communicate.return_value = ["", ""]

        command = ['/bin/true']
        cwd = "/bin/other"
        thd = CommandThread(command, delegate=None, cwd=cwd)
        thd.start()
        thd.join()

        assert Popen_mock.called
        Popen_mock.assert_called_once_with(command, cwd=cwd, bufsize=1, stderr=-1,
                                           stdin=-3, stdout=-1, universal_newlines=True)

    def test_stdout_callback(self):
        echo_string = 'hello world'
        delegate = LoggerDelegate()
        command = ['echo', '-n', echo_string]

        thd = CommandThread(command, delegate=delegate)
        thd.start()
        thd.join()

        assert delegate.stdout_line_call_count == 1
        assert delegate.stdout_buffer == [echo_string]
        assert delegate.rc == 0

    def test_stderr_callback(self):
        echo_string = 'hello world'
        delegate = LoggerDelegate()
        command = ['sh', '-c', "'%(echo)s' -n '%(str)s' >&2" % {
            'echo': shutil.which('echo') or 'echo',  # fallback to built-in (or whatever "echo" in the shell is)
            'str': echo_string
        }]

        thd = CommandThread(command, delegate=delegate)
        thd.start()
        thd.join()

        assert delegate.stdout_line_call_count == 0
        assert delegate.stderr_line_call_count == 1
        assert delegate.stderr_buffer == [echo_string]
        assert delegate.rc == 0

    def test_return_value(self):
        commands = [
            # fallback to shell built-ins
            ([shutil.which('true') or 'true'], 0),
            ([shutil.which('false') or 'false'], 1)
        ]

        for command, rc in commands:
            delegate = LoggerDelegate()
            thd = CommandThread(command, delegate=delegate)
            thd.start()
            thd.join()

            assert delegate.rc == rc


class ReadOutputThreadTest(TestCase):
    def test_stdout_callback(self):
        pass

    def test_stderr_callback(self):
        pass

    def test_stop(self):
        pass
