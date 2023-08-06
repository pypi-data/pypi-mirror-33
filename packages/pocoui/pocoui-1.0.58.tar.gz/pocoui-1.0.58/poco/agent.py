# coding=utf-8

from poco.sdk.interfaces.hierarchy import HierarchyInterface
from poco.sdk.interfaces.input import InputInterface
from poco.sdk.interfaces.screen import ScreenInterface
from poco.sdk.interfaces.command import CommandInterface

__author__ = 'lxn3032'


def _assign(val, default_val):
    if isinstance(val, type(None)):
        return default_val
    else:
        return val


class PocoAgent(object):
    """
    This is the agent class for poco to communicate with target device.

    This class is an aggregation of 4 major interfaces for now.

    - :py:class:`HierarchyInterface <poco.sdk.interfaces.hierarchy.HierarchyInterface>`: defines the hierarchy
      accessibility methods such as dump(crawl the whole UI tree), getAttr(retrieve attribute value by name)
    - :py:class:`InputInterface <poco.sdk.interfaces.input.InputInterface>`: defines the simulated input methods to
      allow inject simulated input on target device
    - :py:class:`ScreenInterface <poco.sdk.interfaces.screen.ScreenInterface>`: defines methods to access the screen
      surface
    - :py:class:`CommandInterface <poco.sdk.interfaces.command.CommandInterface>`: defines methods to communicate
      with target device in arbitrary way. This is optional.
    """

    def __init__(self, hierarchy, input, screen, command=None):
        self.hierarchy = _assign(hierarchy, HierarchyInterface())
        self.input = _assign(input, InputInterface())
        self.screen = _assign(screen, ScreenInterface())
        self.command = _assign(command, CommandInterface())

    def get_sdk_version(self):
        pass

    def rpc_reconnect(self):
        self.rpc.close()
        self.rpc.connect()

    @property
    def rpc(self):
        raise NotImplementedError('This poco agent does not have a explicit rpc connection.')
