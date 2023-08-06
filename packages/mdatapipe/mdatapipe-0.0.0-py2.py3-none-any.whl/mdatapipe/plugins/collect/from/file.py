#!/usr/bin/python
"""
    This plugin reads data from a file, and outputs an item for each line

- collect:
    - from:
        - file:
            path: /tmp/large_access_log     # the file pathname
            only_changes: True              # Only sent lines appended after the last check

"""
import gzip
from time import time
from glob import glob
from os import stat
from os.path import expanduser
from mdatapipe.plugin import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_load(self):
        self.last_modified_time = None
        self.last_position = 0

    def on_input(self, item):  # NOQA
        only_changes = self.config.get('only_changes', False)
        headers_always = self.config.get("headers_always", False)

        path = expanduser(self.config['path'])
        if '*' in path:
            path = glob(path)[-1]
        statbuf = stat(path)
        last_modified_time = statbuf.st_mtime
        file_size = statbuf.st_size

        if path.endswith('.gz'):
            open_func = gzip_open
        else:
            open_func = regular_open

        # If only changes are required, dont't do nothing in first run
        if only_changes and self.last_modified_time is None:
            self.last_modified_time = last_modified_time
            self.last_position = file_size
            # This is required for IIS logs, to get the field names from header
            if headers_always:
                with open_func(path) as data_file:
                    line = data_file.readline()
                    while line and line[0] == "#":
                        line = line.strip('\r\n')
                        self.put(line)
                        line = data_file.readline()
            return

        if only_changes:
            # File was not changed since previous execution
            if last_modified_time == self.last_modified_time and file_size == self.last_position:
                return

        self.last_modified_time = last_modified_time

        start_time = time()
        self.processed_count = 0
        try:
            with open_func(path) as data_file:
                # If this is a rerun start from previous position
                if only_changes:
                    self._seek_last_position(data_file)
                line = data_file.readline()
                while line:
                    self.refresh_status()
                    line = line.strip('\r\n')
                    self.put(line)
                    self.processed_count += 1
                    line = data_file.readline()
                    self.last_position = data_file.tell()
                    self.elapsed_time = time() - start_time
        except IOError:
            raise

    def _seek_last_position(self, file):
        """
        Check if there are any changes to the file since last run
        @return: True if changes are found, False if not
        """
        file.seek(0, 2)                         # go to end of file
        last_position = file.tell()
        if self.last_position > last_position:  # Smaller file was found, truncated ?
            self.last_position = 0
        file.seek(self.last_position)


def regular_open(x):
    return open(x, 'r')


def gzip_open(x):
    return gzip.open(x, 'r')
