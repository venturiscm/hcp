from collections import OrderedDict

from django.conf import settings

from utility.data import ensure_list, sorted_keys

import copy


class AppOptions(object):

    def __init__(self, command):
        self.command = command
        self._options = {}

        self.parser_spec = settings.MANAGER.get_spec('plugin.parser.providers')
        self.parsers = OrderedDict()

        providers = self.command.manager.index.get_plugin_providers('parser', True)

        for name in sorted_keys(self.parser_spec, 'weight'):
            spec = self.parser_spec[name]
            if spec.get('interpolate', True):
                self.parsers[name] = providers[name]('parser', name, self.command, spec)


    def __getitem__(self, name):
        return self._options.get(name, None)

    def __setitem__(self, name, value):
        self._options[name] = value


    def initialize(self, reset = False):
        for name, parser in self.parsers.items():
            parser.initialize(reset)

    def interpolate(self, value, config = None, config_value = True, config_default = False, **options):
        for name, parser in self.parsers.items():
            if not config or parser.config.get(config, config_default) == config_value:
                value = parser.interpolate(value, options)
        return value


    def get(self, name, default = None):
        return self._options.get(name, default)

    def add(self, name, value, interpolate = True):
        if interpolate:
            env = self.command.get_env()

        if interpolate and self.command.interpolate_options():
            self.initialize()
            self._options[name] = self.interpolate(value)
        else:
            self._options[name] = value

        return self._options[name]

    def remove(self, name):
        return self._options.pop(name)

    def clear(self):
        self._options.clear()

    def export(self):
        return copy.deepcopy(self._options)
