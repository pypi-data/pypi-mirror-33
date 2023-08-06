import json
import logging

from qborg.util.commandthread import ICommandDelegate

_logger = logging.getLogger(__name__)


class IODelegate(ICommandDelegate):
    def __init__(self, adapter, delegate):
        self.adapter = adapter
        self.delegate = delegate
        self.line_buffer = ''

    def stdout_line(self, line):
        self.line_buffer += line

    def stderr_line(self, line):
        # _logger.debug(line)
        try:
            json_dict = json.loads(line)

            self.adapter.delegate_call(self.delegate, 'json_output', json_dict)

            # Pass expected log lines to delegate
            message_type = json_dict['type']
            if message_type in ['log_message', 'progress_message', 'archive_progress', 'progress_percent']:
                self.adapter.delegate_call(self.delegate, message_type, json_dict)
        except json.JSONDecodeError:
            pass

    def process_terminated(self, rc):
        self.adapter.delegate_call(self.delegate, 'process_finished', {'rc': rc})
