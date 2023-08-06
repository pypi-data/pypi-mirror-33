# encoding: utf-8

from uiutil import BaseFrame, standalone, Position, RadioButton


class MyFrame(BaseFrame):
    def __init__(self,
                 **kwargs):
        super(MyFrame, self).__init__(**kwargs)

        RadioButton(text="First")

        RadioButton(text="Second", column=Position.NEXT)

        RadioButton(text="Third", column=Position.NEXT)


standalone(frame=MyFrame,
           title="Welcome to UI Util app")
