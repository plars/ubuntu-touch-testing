"""Application classes used to drive them easily with autopilot."""

from autopilot.input import Keyboard, Mouse, Pointer, Touch
from autopilot.platform import model


class App(object):

    """Application class with common code."""

    def __init__(self, tc):
        self.tc = tc
        self.app = None
        self.window = None

        self.keyboard = Keyboard.create()
        if model() == 'Desktop':
            input_device = Mouse.create()
        else:
            input_device = Touch.create()
        self.pointer = Pointer(input_device)
