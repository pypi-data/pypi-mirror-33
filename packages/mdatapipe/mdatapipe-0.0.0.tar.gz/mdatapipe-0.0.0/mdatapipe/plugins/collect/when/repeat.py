#!/usr/bin/python
from time import time, sleep
from mdatapipe.plugin import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_input(self, item):
        start_time = item

        interval = self.config['interval']
        interval = self._time2seconds(interval)
        count = self.config.get('count', None)
        repeat_forever = count is None

        self.put_all(start_time)
        if not repeat_forever:
            count -= 1
        while repeat_forever or count > 0:
            sleep(interval)
            self.put_all(time())
            if not repeat_forever:
                count -= 1

    def _time2seconds(self, value):
        SECONDS_MAP = {'s': 1, 'm': 60, 'h': 60*60, 'd': 24 * 60 * 60}
        number = ''
        unit = 's'
        for char in value:
            if char.isdigit():
                number += char
            else:
                unit = char
                break
        multiplier = SECONDS_MAP[unit]
        return int(number) * multiplier
