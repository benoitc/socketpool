# -*- coding: utf-8 -
#
# This file is part of socketpool.
# See the NOTICE for more information.

import errno
import os
import select
import socket
import sys

try:
    from importlib import import_module
except ImportError:
    import sys

    def _resolve_name(name, package, level):
        """Return the absolute name of the module to be imported."""
        if not hasattr(package, 'rindex'):
            raise ValueError("'package' not set to a string")
        dot = len(package)
        for x in range(level, 1, -1):
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


def is_connected(skt):
    try:
        fno = skt.fileno()
    except socket.error as e:
        if e[0] == errno.EBADF:
            return False
        raise

    try:
        if hasattr(select, "epoll"):
            ep = select.epoll()
            ep.register(fno, select.EPOLLOUT | select.EPOLLIN)
            events = ep.poll(0)
            for fd, ev in events:
                if fno == fd and \
                        (ev & select.EPOLLOUT or ev & select.EPOLLIN):
                    ep.unregister(fno)
                    return True
            ep.unregister(fno)
        elif hasattr(select, "poll"):
            p = select.poll()
            p.register(fno, select.POLLOUT | select.POLLIN)
            events = p.poll(0)
            for fd, ev in events:
                if fno == fd and \
                        (ev & select.POLLOUT or ev & select.POLLIN):
                    p.unregister(fno)
                    return True
            p.unregister(fno)
        elif hasattr(select, "kqueue"):
            kq = select.kqueue()
            events = [
                select.kevent(fno, select.KQ_FILTER_READ, select.KQ_EV_ADD),
                select.kevent(fno, select.KQ_FILTER_WRITE, select.KQ_EV_ADD)
            ]
            kq.control(events, 0)
            kevents = kq.control(None, 4, 0)
            for ev in kevents:
                if ev.ident == fno:
                    if ev.flags & select.KQ_EV_ERROR:
                        return False
                    else:
                        return True

            # delete
            events = [
                select.kevent(fno, select.KQ_FILTER_READ, select.KQ_EV_DELETE),
                select.kevent(fno, select.KQ_FILTER_WRITE, select.KQ_EV_DELETE)
            ]
            kq.control(events, 0)
            kq.close()
            return True
        else:
            r, _, _ = select.select([fno], [], [], 0)
            if not r:
                return True

    except IOError:
        pass
    except (ValueError, select.error,) as e:
        pass

    return False
