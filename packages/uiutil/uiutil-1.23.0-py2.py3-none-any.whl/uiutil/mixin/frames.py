# encoding: utf-8

import logging_helper
from uiutil.helper.introspection import calling_base_frame
from ..helper.arguments import grid_and_non_grid_kwargs
from .all import AllMixIn

logging = logging_helper.setup_logging()


class FramesMixIn(object):

    def __init__(self,
                 *args,
                 **kwargs):

        self._frames = []

    def register_frame(self,
                       frame_object):
        if frame_object not in self._frames:
            self._frames.append(frame_object)

    def add_frame(self,
                  frame,
                  **kwargs):
        try:
            frame_object = frame(**kwargs)
        except Exception as e:
            logging.error(u'There was a problem initialising {frame}'
                          .format(frame=frame))
            logging.exception(e)
            frame_object = None
        return frame_object

    def update_geometry(self):
        """ Pass update geometry request to window this frame is a part of. """
        self.parent.update_geometry()

    def exit_frames(self):
        for frame in self._frames:
            try:
                frame.exit()

            except Exception as err:
                logging.error(u'Something went wrong while exiting frame: {f}'.format(f=frame))
                logging.error(err)