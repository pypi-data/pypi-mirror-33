# -*- coding: utf-8 -*-

from uiutil.tk_names import ttk, HORIZONTAL, EW
from uiutil.helper.arguments import COLUMN_SPAN, ROW_SPAN, COLUMN, ROW, Position
from .base_widget import BaseWidget


class Separator(BaseWidget):
    WIDGET = ttk.Separator
    STYLE = u"TSeparator"
    VAR_PARAM = None
    VAR_TYPE = None

    def __init__(self,
                 orient=HORIZONTAL,
                 sticky=EW,
                 padx=5,
                 pady=5,
                 *args,
                 **kwargs):
        """
        Note: If the label text is static, you can use the 'text' parameter to initialise it.
        In that case, you don't need to store the label object in your frame.
        If you need to change the label text dynamically, you need to store the label object
        in your frame and you should initialise with the initial_text parameter.

        :param args: 
        :param kwargs: 
        """
        span_arg, vector = (COLUMN_SPAN, ROW) if orient == HORIZONTAL else (ROW_SPAN, COLUMN)

        kwargs[span_arg] = kwargs.get(span_arg, Position.MAX)
        kwargs[vector] = kwargs.get(vector, Position.NEXT)

        super(Separator, self).__init__(orient=orient,
                                        sticky=sticky,
                                        padx=padx,
                                        pady=pady,
                                        *args,
                                        **kwargs)
