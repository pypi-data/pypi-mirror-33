"""
This plugin replaces the content of fields with a value:
The replacement rules must be provided in collection:
    { name: field_name, with: text"
    If the filed_name value matches regex, the complete filed is replaced with "text"

Example:

- transform:
    - how:
        - field_replace:
            - { name: Status, with: Ok }
"""
from mdatapipe.plugin import PipelinePlugin


class Plugin(PipelinePlugin):

    def run(self):
        self.input_loop(self.field_replace)

    def field_replace(self, item):
        for key, value in self.config.items():
            item[key] = value
        self.put(item)
