"""Custom matchers used by the tests."""

from autopilot.matchers import Eventually as EventuallyMatcher
from testtools.matchers import Mismatch


def Eventually(matcher):
    """Wrapper around autopilot.matchers.Eventually.

    The aim of the wrapper is just use a different timeout default

    :param matcher: A testools-like matcher that tests the desired condition
    :type matcher: object
    :returns: A value depending on the matcher protocol
    :rtype: None | a mismatch object with information about the mismatch

    """
    return EventuallyMatcher(matcher, timeout=40)


class DoesNotChange(object):
    """Match if two consecutive values are equal."""
    def __init__(self):
        self.old_value = None
        self.value = None

    def __str__(self):
        return 'DoesNotChange()'

    def match(self, value):
        self.old_value = self.value
        self.value = value
        if self.value != self.old_value:
            return Mismatch('Current value ({}) does not match old value ({})'
                            .format(self.value, self.old_value))

        return None
