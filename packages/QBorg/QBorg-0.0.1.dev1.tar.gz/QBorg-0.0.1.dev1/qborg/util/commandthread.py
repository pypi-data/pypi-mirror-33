import threading
import subprocess


class CommandThread(threading.Thread):
    def __init__(self, command_list, delegate=None, cwd=None):
        super().__init__()

        if not isinstance(command_list, list):
            raise TypeError('command_list must be an argv list')

        self.command = command_list
        self._delegate = delegate
        self._cwd = cwd

    def _run_command(self):
        stdout_reader = stderr_reader = None

        with subprocess.Popen(self.command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              bufsize=1, universal_newlines=True, cwd=self._cwd) as process:
            if isinstance(self._delegate, ICommandDelegate):
                stdout_reader = ReadOutputThread('STDOUT reader', process.stdout,
                                                 self._delegate.stdout_line)
                stderr_reader = ReadOutputThread('STDERR reader', process.stderr,
                                                 self._delegate.stderr_line)

                stdout_reader.start()
                stderr_reader.start()

            result = process.communicate()
            rc = process.returncode

            if stdout_reader is not None:
                stdout_reader.stop()
            if stderr_reader is not None:
                stderr_reader.stop()

            if stdout_reader is not None:
                stdout_reader.join()
            if stderr_reader is not None:
                stderr_reader.join()

            # handle possible remaining lines
            for line in result[0].splitlines():
                try:
                    self._delegate.stdout_line(line)
                except Exception:
                    pass
            for line in result[1].splitlines():
                try:
                    self._delegate.stderr_line(line)
                except Exception:
                    pass

        return rc

    def run(self):
        rc = self._run_command()
        try:
            self._delegate.process_terminated(rc)
        except Exception:
            pass


class ReadOutputThread(threading.Thread):
    def __init__(self, name, pipe, callback):
        threading.Thread.__init__(self, name=name)
        self.pipe = pipe
        self.callback = callback
        self.stopped = False

    def run(self):
        while not self.stopped:
            try:
                line = self.pipe.readline()
                if line:
                    try:
                        self.callback(line)
                    except Exception:
                        pass
            except (EOFError, ValueError):
                pass

    def stop(self):
        self.stopped = True


class ICommandDelegate():
    def stdout_line(self, line):
        pass

    def stderr_line(self, line):
        pass

    def process_terminated(self, rc):
        pass
