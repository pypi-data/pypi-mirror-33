# -*- coding: utf-8 -*-

import logging_helper
from uiutil.tk_names import ttk
from .base_widget import BaseWidget, READONLY
from ..helper.arguments import pop_kwarg
from collections import Mapping

logging = logging_helper.setup_logging()


class ValueMappedCombobox(BaseWidget):
    WIDGET = ttk.Combobox
    STYLE = u"TCombobox"
    VAR_TYPE = u'string_var'
    VAR_PARAM = u'textvariable'
    VAR_IS_OPTIONAL = False

    @staticmethod
    def sorted_except_first_value(values):
        return values[:1] + sorted(values[1:])

    def __init__(self,
                 # enabled_state=READONLY,
                 # sort=True,
                 *args,
                 **kwargs):
        # Default enabled state is readonly.
        # That prevents editing, which seems
        # to be the most common case for a
        # Combobox.
        kwargs[u'enabled_state'] = kwargs.get(u'enabled_state', READONLY)
        kwargs[u'state'] = kwargs.get(u'state', kwargs[u'enabled_state'])
        values = kwargs.get(u'values')
        value = kwargs.get(u'value')

        self.sort = pop_kwarg(kwargs, u'sort', True)
        self.store_value_map(values)
        if self.sort and values:
            kwargs[u'values'] = self.sort_values(values)

        super(Combobox, self).__init__(*args, **kwargs)

        if not values:
            values = [u""]
        if not value:
            try:
                self.value = values[0]
            except KeyError:
                self.value = values.keys()[0]

    def store_value_map(self,
                        values):
        if not values:
            values = {}  # No values yet
        if not isinstance(values, Mapping):
            values = {value: value for value in values}
        self.value_map = values

    def sort_values(self,
                    values):
        values = list(values)
        if self.sort is True:
            values.sort()
        elif self.sort:
            values = self.sort(values)
        return values

    def lookup_by_key_or_value(self,
                               key_or_value):

        # Match to the key
        if key_or_value in self.value_map:
            return key_or_value

        # Associated value may have been supplied. Return the key
        for key, value in iter(self.value_map.items()):
            if value == key_or_value:
                return key

        # Not found - new value
        try:
            key, value = key_or_value
        except (TypeError, ValueError):
            key = value = key_or_value

        self.value_map[key] = value
        self.values = list(self.values) + [key]

        return key_or_value  # New value

    @property
    def value(self):
        try:
            return self.value_map[self._var.get()]
        except AttributeError:
            self.raise_missing_variable_error()
        except KeyError:
            pass

    @value.setter
    def value(self,
              key_or_value):
        try:
            # TODO: Figure out if we need to use value or key
            #       currently assume value is a key
            self._var.set(self.lookup_by_key_or_value(key_or_value))
        except AttributeError:
            self.raise_missing_variable_error()

    @property
    def values(self):
        return self.widget[u'values']

    @values.setter
    def values(self,
               values):
        self.store_value_map(values)
        self.config(values=self.sort_values(self.value_map.keys()))
