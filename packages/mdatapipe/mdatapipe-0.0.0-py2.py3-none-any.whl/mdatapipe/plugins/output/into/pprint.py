#!/usr/bin/python

# absolute_import is needed to import the builtin pprint insteaf of our own module

from __future__ import absolute_import
from pprint import pprint
from mdatapipe.plugin import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_input(self, item):
        pprint(item)
