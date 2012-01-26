# -*- coding: utf-8 -
#
# This file is part of socketpool.
# See the NOTICE for more information.

try:
    from importlib import import_module
except ImportError:
    import sys

    def _resolve_name(name, package, level):
        """Return the absolute name of the module to be imported."""
        if not hasattr(package, 'rindex'):
            raise ValueError("'package' not set to a string")
        dot = len(package)
        for x in xrange(level, 1, -1):
            try:
                dot = package.rindex('.', 0, dot)
            except ValueError:
                raise ValueError("attempted relative import beyond top-level "
                                  "package")
        return "%s.%s" % (package[:dot], name)


    def import_module(name, package=None):
        """Import a module.

        The 'package' argument is required when performing a relative import. It
        specifies the package to use as the anchor point from which to resolve the
        relative import to an absolute import.

        """
        if name.startswith('.'):
            if not package:
                raise TypeError("relative imports require the 'package' argument")
            level = 0
            for character in name:
                if character != '.':
                    break
                level += 1
            name = _resolve_name(name[level:], package, level)
        __import__(name)
        return sys.modules[name]

def load_backend(backend_name):
    """ load pool backend. If this is an external module it should be
    passed as "somelib.backend_mod", for socketpool backend you can just
    pass the name.

    Supported backend are :
        - thread: connection are maintained in a threadsafe queue.
        - gevent: support gevent
        - eventlet: support eventlet

    """
    try:
        if len(backend_name.split(".")) > 1:
            mod = import_module(backend_name)
        else:
            mod = import_module("socketpool.backend_%s" % backend_name)
        return mod
    except ImportError:
        error_msg = "%s isn't a socketpool backend" % backend_name
        raise ImportError(error_msg)
