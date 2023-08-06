"""
Tools module.

By default, only tools that are listed in the configuration are
loaded automatically. See configuration variables:
 *_PLUGINS_AUTOLOAD
 *_PLUGINS_TOOLS

"""
import logging
import importlib

from benchbuild.settings import CFG

LOG = logging.getLogger(__name__)


def discover():
    """
    Import all experiments listed in PLUGINS_EXPERIMENTS.

    Tests:
        >>> from benchbuild.settings import CFG
        >>> from benchbuild.tools import discover
        >>> import logging as lg
        >>> import sys
        >>> l = lg.getLogger('benchbuild')
        >>> lg.getLogger('benchbuild').setLevel(lg.DEBUG)
        >>> lg.getLogger('benchbuild').handlers = [lg.StreamHandler(stream=sys.stdout)]
        >>> CFG["plugins"]["tools"] = ["benchbuild.non.existing", "benchbuild.tools.uchroot"]
        >>> discover()
        Could not find 'benchbuild.non.existing'
        ImportError: No module named 'benchbuild.non'
    """
    if CFG["plugins"]["autoload"].value():
        experiment_plugins = CFG["plugins"]["tools"].value()
        for exp_plugin in experiment_plugins:
            try:
                importlib.import_module(exp_plugin)
            except ImportError as import_error:
                LOG.error("Could not find '%s'", exp_plugin)
                LOG.error("ImportError: %s", import_error.msg)
