# encoding: utf-8

from uiutil import BaseFrame, standalone, Label, Position, RadioButton


class MyFrame(BaseFrame):
    def __init__(self,
                 **kwargs):
        super(MyFrame, self).__init__(**kwargs)

        self.radio = RadioButton(text="First",
                                 value="1",
                                 command=self.set_label)

        RadioButton(text="Second",
                    value="2",
                    column=Position.NEXT)

        RadioButton(text="Third",
                    column=Position.NEXT)

        self.label = Label(row=Position.NEXT,
                           column=Position.START,
                           columnspan=3,
                           value="?")
        self.radio.value = "2"
        self.set_label()

    def set_label(self):
        self.label.value = "{value} selected".format(value=self.radio.value)


standalone(frame=MyFrame,
           title="Welcome to UI Util app")
