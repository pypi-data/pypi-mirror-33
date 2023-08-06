#!/usr/bin/python


from mdatapipe.plugin import PipelinePlugin


class Plugin(PipelinePlugin):

    def run(self):
        skip_lines = int(self.config.get("lines", 0))
        while skip_lines > 0:
            self.get()
            skip_lines -= 1
        self.input_loop(self.pass_value)

    def pass_value(self, value):
        self.put(value)
