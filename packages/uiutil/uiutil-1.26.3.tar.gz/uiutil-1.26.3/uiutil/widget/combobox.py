# -*- coding: utf-8 -*-

from uiutil.tk_names import ttk
from .base_widget import BaseWidget, READONLY
from ..helper.arguments import pop_kwarg


class Combobox(BaseWidget):
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
                 # sort=False,
                 *args,
                 **kwargs):
        # Default enabled state is readonly.
        # That prevents editing, which seems
        # to be the most common case for a
        # Combobox.
        kwargs[u'enabled_state'] = kwargs.get(u'enabled_state', READONLY)
        kwargs[u'state'] = kwargs.get(u'state', kwargs[u'enabled_state'])
        values = kwargs.get(u'values')
        self.sort = pop_kwarg(kwargs, u'sort', False)
        if self.sort and values:
            kwargs[u'values'] = self.sort_values(values)

        super(Combobox, self).__init__(*args, **kwargs)

        if values and not self.value:
            self.value = values[0]

    def sort_values(self,
                    values):
        values = list(values)
        if self.sort is True:
            values.sort()
        elif self.sort:
            values = self.sort(values)
        return values

    @property
    def values(self):
        return self.widget[u'values']

    @values.setter
    def values(self,
               values):
        self.config(values=self.sort_values(values))

    def current(self,
                idx=None):
        return self.widget.current(idx)
