"""
This plugin replaces the content of fields when their values match a regex expression.
The replacement rules must be provided in a list like:
    { name: field_name, find: regex, replace_with: text" }
    If the filed_name value matches regex, the complete filed is replaced with "text"

Example:

- transform:
    - how:
        - field_regex:
            - { name: uri, find: ^/app1/, replace_with: APP1 }
"""
from mdatapipe.plugin import PipelinePlugin
import re


class Plugin(PipelinePlugin):

    def on_load(self):
        self.regex_dict = {}  # Use a dict to associate rules with field names
        for config_item in self.config:
            field_name = config_item['name']
            match_re = re.compile(config_item['match'])
            regex_list = self.regex_dict.get(field_name, [])
            self.regex_dict[field_name] = regex_list
            replace_with_text = config_item.get('replace_with')
            if replace_with_text:
                regex_list.append((match_re, replace_with_text))
            if config_item.get('delete', False):
                regex_list.append((match_re, None))

    def on_input(self, item):
        for field_name, field_rules in self.regex_dict.items():
            value = item.get(field_name, None)
            if value is None:  # Field has no regex rule
                continue
            for rule in field_rules:
                find_re, replace_with_text = rule
                if find_re.match(value):
                    if replace_with_text is None:  # Matches with a delete rule
                        return
                    item[field_name] = replace_with_text
                    break
        self.put(item)

    def replace_with(self, field_value, text):
        return text
