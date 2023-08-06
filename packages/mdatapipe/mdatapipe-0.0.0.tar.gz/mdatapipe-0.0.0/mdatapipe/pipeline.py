# -*- coding: utf-8 -*-
from __future__ import print_function
from time import time, sleep
from yaml import load
from os.path import join
from mdatapipe.plugin import load_plugin_module
from multiprocessing import Pipe
from mdatapipe.plugin import PipelinePlugin


class StartPlugin(PipelinePlugin):
    """
    The start plugin delives the current time to every plugin process of the next stage.
    The first stage defined on the pipeline will receive this value and start it's work
    """
    _not_started = True

    def on_input(self, value):
        self.put_all(time())
        self.put_all(None)

    def get(self):
        if self._not_started:
            self._not_started = False
            return time()
        else:
            return None


class Pipeline(object):

    def __init__(self, data=None, file=None, parallel=None):
        """ Load data pipeline definition from file """
        self.stages = []  # A stage in a pipeline is group of «parallell» processes
        self.file = file

        # If data is None read data from file
        if data is None:
            with open(file, 'r') as data_file:
                data = data_file.read()

        # Load YAML text data into a python object
        self.pipeline_data = load(data)

        # Parse parallel control arguments
        self.parallel_rules = self._parse_rules(parallel)

        # The start plugin outputs a single value with the current time
        # The "collect/when" plugin wil start when this value is received
        start_plugin = StartPlugin("_StartPlugin")
        self.add_stage([start_plugin])

        # Load all plugins
        self._load_plugins()

        # Setup control pipes
        self._setup_control_pipes()

        # Setup pipes between plugins
        self._setup_pipes()

    def _load_plugins(self):
        """
        Load and init all pipeline plugins as declared in the pipeline description
        """
        if not isinstance(self.pipeline_data, list):
            raise Exception("Expecting list element, got " + str(self.pipeline_data))
        for op_group_item in self.pipeline_data:
            for op_group, op_type_list in op_group_item.items():
                    for op_type_item in op_type_list:
                        for op_type, op_type_list in op_type_item.items():
                            for op_driver_item in op_type_list:
                                # Drivers without config
                                if not isinstance(op_driver_item, dict):
                                    op_driver_item = {op_driver_item: None}
                                for op_driver, op_config in op_driver_item.items():
                                    self._load_plugin(op_group, op_type, op_driver, op_config)

        # Append the pprint plugin if no output plugin was provided
        if op_group != 'output':
            self._load_plugin("output", "into", "pprint", None)

    def _load_plugin(self, op_group, op_type, op_driver, op_config):
        """ Init a plugin associated with a stage """
        stage_processes = []
        module_name = join(op_group, op_type, op_driver+".py")
        process_count = self.parallel_rules.get(module_name, 1)
        for process_nr in range(process_count):
            process_name = module_name + " - #" + str(process_nr)
            plugin = load_plugin_module(op_group, op_type, op_driver, op_config)
            plugin.name = process_name
            stage_processes.append(plugin)
        self.add_stage(stage_processes)

    def _setup_control_pipes(self):
        """ Setup pipes between stages/processes """
        self.control_sender_list = []
        self.control_receiver_list = []

        for i in range(len(self.stages)):
            current_stage = self.stages[i]
            for current_process in current_stage:

                receiver, sender = Pipe(duplex=False)
                current_process.setup_control_receiver(receiver)
                self.control_sender_list.append(sender)

                receiver, sender = Pipe(duplex=False)
                current_process.setup_control_sender(sender)
                self.control_receiver_list.append(receiver)

    def _setup_pipes(self):
        """ Setup pipes between stages/processes """
        for i in range(len(self.stages) - 1):
            current_stage = self.stages[i]
            next_stage = self.stages[i+1]
            for current_process in current_stage:
                for next_process in next_stage:
                    receiver, sender = Pipe(duplex=True)
                    # Senders from this stage, are connected
                    # to receivers in the next stage
                    current_process.add_sender(sender)
                    next_process.add_receiver(receiver)

    def start(self, fail):

        self.start_time = time()
        for stage in self.stages:
            for process in stage:
                process.set_fail_on_error(fail)
                process.start()

    def get_stats(self):
        active_processes = 0
        for stage in self.stages:
            for process in stage:
                if process.is_alive():
                    active_processes += 1
        return active_processes

    def kill(self):
        """ Kill all plugin processes """
        for stage in self.stages:
            for process in stage:
                process.terminate()

    def _parse_rules(self, rules_list):
        if rules_list is None:
            return {}

        rules_dict = {}

        for rule in rules_list:
            plugin_name, value = rule.split(':')
            rules_dict[plugin_name] = int(value)

        return rules_dict

    def printTable(self, tbl, borderHorizontal='-', borderVertical='|', borderCross='+'):
        cols = [list(x) for x in zip(*tbl)]
        lengths = [max(map(len, map(str, col))) for col in cols]
        f = borderVertical + borderVertical.join(' {:>%d} ' % l for l in lengths) + borderVertical
        s = borderCross + borderCross.join(borderHorizontal * (l+2) for l in lengths) + borderCross

        print(s)
        for row in tbl:
            print(f.format(*row))
            print(s)

    def add_stage(self, stage):
        self.stages.append(stage)

    def check_status(self, request_status=False):

        if request_status:
            for conn in self.control_sender_list:
                conn.send("status")
            print("-" * 40, self.file)

        for conn in self.control_receiver_list:
            while conn.poll():
                result = conn.recv()
                print(result)

    def wait_end(self):
        while self.get_stats() > 0:
            self.check_status()
            sleep(1)
        print("Elapsed time", time() - self.start_time)
