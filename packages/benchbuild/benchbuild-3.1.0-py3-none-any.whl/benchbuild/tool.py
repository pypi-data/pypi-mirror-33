"""Tools

A tool in benchbuild is similar to a project. However, tools can be declared as
dependencies inside projects and experiments.
A tool implementation is required to provide a way to identify its availability
on the system.
In addition tools should provide a way to install them on the target system.

Example
-------
```python
class HelloTool(Tool):
    pass
```
"""
import copy
import uuid
from abc import abstractmethod

import attr

from benchbuild.settings import CFG


class ToolsRegistry(type):
    """Registry for benchbuild tools."""

    tools = {}

    def __init__(cls, name, bases, dict):
        """Register a project in the registry."""
        super(ToolsRegistry, cls).__init__(name, bases, dict)

        if cls.NAME is not None:
            ToolsRegistry.tools[cls.NAME] = cls


@attr.s(cmp=False)
class Tool(object, metaclass=ToolsRegistry):
    """
    TODO

    Attributes:
        name (str): The name of the tool, defaults to NAME
    """

    NAME = None
    VERSION = None

    def __new__(cls, *args, **kwargs):
        """Create a new experiment instance and set some defaults."""
        del args, kwargs  # Temporarily unused
        new_self = super(Tool, cls).__new__(cls)
        if cls.NAME is None:
            raise AttributeError(
                "{0} @ {1} does not define a NAME class attribute.".format(
                    cls.__name__, cls.__module__))
        return new_self

    name = attr.ib(
        default=attr.Factory(lambda self: type(self).NAME, takes_self=True))

    version = attr.ib(
        default=attr.Factory(lambda self: type(self).VERSION, takes_self=True))

    @abstractmethod
    def available(self):
        """Check, if the given tool is available on the system."""