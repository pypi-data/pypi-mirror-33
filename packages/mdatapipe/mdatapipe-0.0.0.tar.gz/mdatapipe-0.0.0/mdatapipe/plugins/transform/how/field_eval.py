#!/usr/bin/python


from mdatapipe.plugin import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_input(self, item):
        for rule in self.config:
            current_val = item.get(rule['name'], None)
            if current_val:
                new_val = eval("current_val." + rule['expr'])
                item[rule['name']] = new_val
        self.put(item)
