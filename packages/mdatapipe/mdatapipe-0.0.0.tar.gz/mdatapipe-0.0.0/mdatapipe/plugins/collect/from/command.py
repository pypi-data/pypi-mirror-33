#!/usr/bin/python
import sys
import os
from mdatapipe.plugin import PipelinePlugin
is_py2 = sys.version[0] == '2'
if is_py2:
    from commands import getstatusoutput
else:
    from subprocess import getstatusoutput  # pylint: disable=E0611


class Plugin(PipelinePlugin):

    def on_input(self, item):
        print("Executing ", item)
        cmd = self.config['cmd']
        for env_item in self.config.get('env', []):
            items = env_item.items()
            for key, value in items:
                os.environ[key] = value
        status, output = getstatusoutput(cmd)
        if status != 0:
            print(output)
            raise Exception("Error %d on command!" % status)
        self.put(output)
