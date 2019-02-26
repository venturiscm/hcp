from systems.command import args
from utility import text, data

import re
import copy
import json


class DataMixin(object):

    def parse_flag(self, name, flag, help_text):
        self.add_schema_field(name, 
            args.parse_bool(self.parser, name, flag, help_text), 
            True
        )

    def parse_variable(self, name, optional, type, help_text, value_label = None, default = None):
        if optional and isinstance(optional, str):
            if not value_label:
                value_label = name
            
            self.add_schema_field(name,
                args.parse_option(self.parser, name, value_label.upper(), optional, type, help_text, default),
                True
            )
        else:
            self.add_schema_field(name, 
                args.parse_var(self.parser, name, type, help_text, optional), 
                optional
            )

    def parse_variables(self, name, optional, type, help_text, value_label = None, default = None):
        if optional and isinstance(optional, str):
            help_text = "{} (comma separated)".format(help_text)

            if not value_label:
                value_label = name

            self.add_schema_field(name,
                args.parse_csv_option(self.parser, name, value_label.upper(), optional, help_text, default),
                True
            )
        else:
            self.add_schema_field(name,
                args.parse_vars(self.parser, name, type, help_text, optional),
                optional
            )

    def parse_fields(self, facade, name, optional = False, excluded_fields = [], help_callback = None, callback_args = [], callback_options = {}):
        if facade:
            required_text = [x for x in facade.required if x not in list(excluded_fields)]
            optional_text = [x for x in facade.optional if x not in excluded_fields]
            help_text = "\n".join(text.wrap("fields as key value pairs\n\nrequirements: {}\n\noptions: {}".format(", ".join(required_text), ", ".join(optional_text)), 60))
        else:
            help_text = "\nfields as key value pairs\n"

        if help_callback and callable(help_callback):
            help_text += "\n".join(help_callback(*callback_args, **callback_options))

        self.add_schema_field(name,
            args.parse_key_values(self.parser, name, 'field=VALUE', help_text, optional),
            optional
        )


    def parse_test(self):
        self.parse_flag('test', '--test', 'test execution without permanent changes')

    @property
    def test(self):
        return self.options.get('test', False)


    def parse_force(self):
        self.parse_flag('force', '--force', 'force execution even with provider errors')

    @property
    def force(self):
        return self.options.get('force', False)


    def parse_clear(self):
        self.parse_flag('clear', '--clear', 'clear all items')

    @property
    def clear(self):
        return self.options.get('clear', False)


    def check_available(self, facade, name, warn = False):
        instance = self.get_instance(facade, name, required = False)
        if instance:
            if warn:
                self.warning("{} {} already exists".format(
                    facade.name.title(),
                    name
                ))
            return False        
        return True

    def check_exists(self, facade, name, warn = False):
        instance = self.get_instance(facade, name, required = False)
        if not instance:
            if warn:
                self.warning("{} {} does not exist".format(
                    facade.name.title(),
                    name
                ))
            return False        
        return True


    def get_instance(self, facade, name, required = True):
        instance = self._get_cache_instance(facade, name)

        if not instance:
            instance = facade.retrieve(name)
            
            if not instance and required:
                self.error("{} {} does not exist".format(facade.name.title(), name))
            else:
                if instance and instance.initialize(self):
                    self._set_cache_instance(facade, name, instance)
                else:
                    return None
        
        return instance


    def get_instances(self, facade, 
        names = [], 
        objects = [], 
        groups = [], 
        states = []
    ):
        search_items = []
        results = {}

        if not names and not groups and not objects and not states:
            search_items = facade.all()
        else:
            states = data.ensure_list(states)
            search_items.extend(data.ensure_list(names))
            search_items.extend(data.ensure_list(objects))

            for group in data.ensure_list(groups):
                search_items.extend(facade.keys(groups__name = group))

        def init_instance(data, state):
            if isinstance(data, str):
                cached = self._get_cache_instance(facade, data)
                if not cached:
                    instance = facade.retrieve(data)
            else:
                instance = data
                cached = self._get_cache_instance(facade, getattr(instance, facade.key()))
            
            if instance:
                name = getattr(instance, facade.key())
                state = getattr(instance, 'state', None)

                if not cached:
                    if instance.initialize(self):
                        self._set_cache_instance(facade, name, instance)
                    else:
                        instance = None
                else:
                    instance = cached
                
                if instance and (not states or not state or state in states):
                    results[name] = instance
            else:
                self.error("{} instance {} does not exist".format(facade.name.title(), data))

        self.run_list(search_items, init_instance)
        return results.values()


    def search_instances(self, facade, queries = [], joiner = 'AND', error_on_empty = True):
        queries = data.ensure_list(queries)
        joiner = joiner.upper()
        results = {}        

        def perform_query(filters, states):
            instances = facade.query(**filters)
            if len(instances) > 0:
                for instance in self.get_instances(facade,
                    objects = list(instances), 
                    states = states
                ):
                    results[getattr(instance, facade.key())] = instance
        
        if queries:
            filters = {}
            states = []

            for query in queries:
                matches = re.search(r'^([^\=]+)\s*\=\s*(.+)', query)

                if matches:
                    field = matches.group(1)
                    value = matches.group(2)

                    if ',' in value:
                        value = value.split(',')
                    
                    if joiner == 'OR':
                        filters = {}
                        states = []

                    if field != 'state':
                        filters[field] = value
                    else:
                        states.append(value)

                    if joiner == 'OR':
                        perform_query(filters, states)                   
                else:
                    self.error("Search filter must be of the format: field[__check]=value".format(query))
        
            if joiner == 'AND':
                perform_query(filters, states)
        else:
            results.extend(self.get_instances(facade))
        
        if error_on_empty and not results:
            if queries:
                self.warning("No {} instances were found: {}".format(facade.name, ", ".join(queries)))
            else:
                self.warning("No {} instances were found".format(facade.name))
        
        return results.values()


    def facade(self, facade):
        if getattr(self, '_facade_cache', None) is None:
            self._facade_cache = {}
        
        if not self._facade_cache.get(facade.name, None):
            self._facade_cache[facade.name] = copy.deepcopy(facade)

        return self._facade_cache[facade.name]


    def _parse_add_remove_names(self, names):
        add_names = []
        remove_names = []
        
        if names:
            for name in names:
                name = re.sub(r'\s+', '', name) 
                matches = re.search(r'^~(.*)$', name)
                if matches:
                    remove_names.append(matches.group(1))
                else:
                    name = name[1:] if name[0] == '+' else name
                    add_names.append(name)
        
        return (add_names, remove_names)


    def _init_instance_cache(self, facade):
        cache_variable = "_data_{}_cache".format(facade.name)

        if not getattr(self, cache_variable, None):
            setattr(self, cache_variable, {})

        return cache_variable
        
    def _get_cache_instance(self, facade, name):
        cache_variable = self._init_instance_cache(facade)
        return getattr(self, cache_variable).get(name, None)

    def _set_cache_instance(self, facade, name, instance):
        cache_variable = self._init_instance_cache(facade)
        getattr(self, cache_variable)[name] = instance
