"""
    A mdatapipe plugin is a regular python module which provides
    a class named "Plugin" derived from the class "PipelinePlugin".

    The load_module() function imports the python module and invokes the
    Plugin's class __init__() method.

    The "PipelinePlugin" base class provides all the methods that a plugin
    can use to interace with the the pipeline, this is in fact the plugin API.

    The current callbacks are available:
        - on_load(self):
        invoked when the plugin is loaded

        - on_validate(self)
        validates that the config is valid and that critical resources are available

        - on_input(self, value):
        invoked when a item is received

        - on_buffer_full(self, buffer):
        invoked when the config contains "buffer_size" and the buffer is full

        - on_stop(self)
        invoked when the plugin is stopped

    The following methods are available:
        - get(item):
        get the next item from the input pipe
        - put(item):
        write an item into the input queue of an instance of the next plugin
        - put_all(value)
        put a value into the input queues of all the instances of the next plugin
"""
from __future__ import print_function
from sys import stderr
from traceback import print_exc
from os.path import join
from time import time
from multiprocessing import Process
from importlib import import_module
from six import string_types


class PipelinePlugin(Process):

    def __init__(self, name, config=None):
        """ Called immeditaly after the plugin is imported """
        super(PipelinePlugin, self).__init__()
        self.name = name
        self.config = config
        self.in_pipe_list = []          # List of input pipes
        self.out_pipe_list = []         # List of output pipes
        self.current_input_index = 0    # Index for the current input pie
        self.current_out_index = 0      # Index for the current output pipe
        self.buffer_size = 1
        self.buffer = []
        self.get_item_count = 0
        self.put_item_count = 0
        self.start_time = None
        self.get_start_time = None
        self._fail_on_error = False
        self.execution_time = 0         # Time spent on callback execution
        self.current_in_conn = None     # Last connection used to get data

        self._set_variable_config_watch(config)
        if config and isinstance(config, dict):
            self.buffer_size = config.get('buffer_size', None)
        if hasattr(self, 'on_input'):
            self.run = self.input_loop
        elif hasattr(self, 'on_input_buffer'):
            self.run = self.input_buffer_loop
        else:
            raise Exception("Plugin misses an on_input() randon_input_buffer()!\n"+self.name)
        if hasattr(self, 'on_load'):
            self.on_load()

    def _set_variable_config_watch(self, config):
        """
        If a config variable is set to %field% we must set a watch
        for the get() method, so that it overrides the config item with
        the field that is obtained from the input pipe
        """
        self._config_watch = {}
        if not config:
            return
        config_list = self.config
        if not isinstance(config_list, list):
            config_list = [config_list]

        for config_item in config_list:
            if isinstance(config_item, dict):
                for config_field_name, field_value in config_item.items():
                    # Using $field_name$
                    if isinstance(field_value, string_types) and field_value[0] == "$" and field_value[-1] == "$":
                            field_name = field_value[1:-1]
                            watch_list = self._config_watch.get(field_name, [])
                            self._config_watch[field_name] = watch_list
                            watch_list.append(config_field_name)

    def input_loop(self):
        self.start_time = None
        self.loop_count = 0
        while True:
            reply = None
            item = self.get()
            if self.start_time is None:
                self.start_time = time()
            if item is None:
                break
            self.loop_count += 1
            execution_stat_time = time()
            try:
                reply = self.on_input(item)
            except:  # NOQA
                print("---------- Plugin on_item execution failed")
                print(self.name)
                print(item)
                if self._fail_on_error:
                    raise
                print_exc(file=stderr)
            finally:
                current_time = time()
                self.execution_time += current_time - execution_stat_time
                self.elapsed_time = current_time - self.start_time
            if reply is not None:
                self.current_in_conn.send(reply)

        # Close all descendents
        self._close_descendents()

        if hasattr(self, 'on_terminate'):
            self.on_terminate()

    def input_buffer_loop(self):
        self.start_time = None
        self.loop_count = 0
        while True:
            # We cannot close descendents because we still
            item = self.get(close_all_descendents=False)
            if self.start_time is None:
                self.start_time = time()
            if item is None:
                break
            self.loop_count += 1
            self.buffer.append(item)
            if len(self.buffer) == self.buffer_size:
                self._flush_input_buffer()

        # Flush remaining entries
        self._flush_input_buffer()

        # Close all descendents
        self._close_descendents()

    def _flush_input_buffer(self):
        execution_stat_time = time()
        try:
            self.on_input_buffer(self.buffer)
        except:  # NOQA
            print("---------- Plugin on_item execution failed")
            print(self.name)
            if self._fail_on_error:
                raise
            print_exc(file=stderr)
        finally:
            self.buffer = []
            current_time = time()
            self.execution_time += current_time - execution_stat_time
            self.elapsed_time = current_time - self.start_time

    def _close_descendents(self):
        if self.execution_time:
            ips = int(self.loop_count / self.execution_time)
            ips = '{:>10}'.format('{:,}'.format(ips))
            execution_time = float(("%0.2f" % self.execution_time))
            loop_count = '{:>8}'.format('{:,}'.format(self.loop_count))
            execution_time = ('{:>6}'.format(execution_time))
            self.report_status("%s items in %s seconds, %s i/s" % (loop_count, execution_time, ips))
        self.put_all(None)

    def put(self, item, wait_for_reply=False):
        if len(self.out_pipe_list) == 0:
            raise Exception("Put() called  without an output pipe")
        self.out_pipe_list[self.current_out_index].send(item)
        if wait_for_reply:
            reply = self.out_pipe_list[self.current_out_index].recv()
            return reply
        self.current_out_index += 1
        if self.current_out_index >= len(self.out_pipe_list):
            self.current_out_index = 0
        self.put_item_count += 1
        self.last_time = time()

    def get(self, close_all_descendents=True):
        """
            Get one element from the input pipes, using round-robin
            If all pipes are closed, raise an EOFError
        """
        if self.run != self.input_loop and self.run != self.input_buffer_loop:
            raise Exception('Calling get() without a "on_input()" method', self)

        while len(self.in_pipe_list) > 0:
            current_in_conn = self.in_pipe_list[self.current_input_index]
            self.current_in_conn = current_in_conn

            # Rotate the current input pipe selection
            self.current_input_index += 1
            if self.current_input_index >= len(self.in_pipe_list):
                self.current_input_index = 0

            item = current_in_conn.recv()
            self.get_item_count += 1
            self.last_time = time()
            self.refresh_status()

            if item is None:
                # Delete current connection from list
                new_in_pipe_list = [conn for conn in self.in_pipe_list if conn != current_in_conn]
                self.in_pipe_list = new_in_pipe_list
                self.current_input_index = 0
                continue

            # Dinamyc update of config based on retrieved objects
            # If a watched field is found in the object
            # Update all config items which use it
            for watch_item, watch_list in self._config_watch.items():
                if watch_item in item:
                    for config_item in watch_list:
                        self.config[config_item] = item[watch_item]
            return item
        return None

    def put_all(self, item):
        """ Put a value in every output pipe"""
        if len(self.out_pipe_list) == 0 and item is not None:
            raise Exception("Unable to put message because there is no output pipe:\n"+self.name)
        for conn in self.out_pipe_list:
            self.put_item_count += 1
            conn.send(item)

    def add_sender(self, connection):
        self.out_pipe_list.append(connection)

    def add_receiver(self, connection):
        self.in_pipe_list.append(connection)

    def setup_control_receiver(self, receiver):
        self.control_receiver = receiver

    def setup_control_sender(self, sender):
        self.control_sender = sender

    def _check_control_pipe(self):
        if self.control_receiver.poll():
            cmd = self.control_receiver.recv()
            if cmd == "status":
                name = ('{:>35}'.format(self.name))
                get_count = (' | Get {:>8}'.format(self.get_item_count))
                put_count = (' | Put {:>8}'.format(self.put_item_count))
                execution_time = float(("%0.2f" % self.execution_time))
                put_count = (' | Exec. {:>8}s'.format(execution_time))
                count = self.put_item_count
                if count == 0:
                    count = self.get_item_count
                if execution_time:
                    ips = count / execution_time
                    ips = int(self.loop_count / self.execution_time)
                    ips = ' | {:>10} i/s '.format('{:,}'.format(ips))
                else:
                    ips = ''
                self.control_sender.send(name + get_count + put_count + ips)

    def refresh_status(self):
        self._check_control_pipe()

    def set_fail_on_error(self, value):
        self._fail_on_error = value

    def report_status(self, message):
        # Silent internal plugins
        if self.name[0] == "_":
            return
        msg = ('{:>35}'.format(self.name))
        self.control_sender.send(msg + " --- " + message)


def load_plugin_module(op_group, op_type, op_driver, op_config):
    """ Load a plugin module """
    # script_dir = dirname(abspath(__file__))
    module_name = join(op_group, op_type, op_driver+".py")
    module_sys_name = '.'.join(['mdatapipe', 'plugins', op_group, op_type, op_driver])
    # module_fname = join(script_dir, 'plugins', module_name)
    try:
        module = import_module(module_sys_name)
    except ImportError:
        print("Unable to import module %s" % module_name)
        raise
    try:
        plugin = module.Plugin(module_name, op_config)
    except AttributeError:
        print("Plugin module '%s' does not provide a Plugin class!" % module_sys_name)
        raise
    return plugin
