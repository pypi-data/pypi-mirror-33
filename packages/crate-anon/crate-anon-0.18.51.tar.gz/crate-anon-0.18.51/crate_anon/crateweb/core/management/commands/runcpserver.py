#!/usr/bin/env python
# crate_anon/crateweb/core/management/commands/runcpserver.py

"""
===============================================================================

    Copyright (C) 2015-2018 Rudolf Cardinal (rudolf@pobox.com).

    This file is part of CRATE.

    CRATE is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    CRATE is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with CRATE. If not, see <http://www.gnu.org/licenses/>.

===============================================================================

Django management command framework for CherryPy based on:
    https://lincolnloop.com/blog/2008/mar/25/serving-django-cherrypy/
    Idea and code snippets borrowed from
        http://www.xhtml.net/scripts/Django-CherryPy-server-DjangoCerise
    Adapted to run as a management command.
Some bugs fixed by RNC.
Then rewritten by RNC.
Then modified to serve CRATE, with static files, etc.
Then daemonizing code removed:
    https://code.djangoproject.com/ticket/4996

TEST COMMAND:
./manage.py runcpserver --port 8080 --ssl_certificate /etc/ssl/certs/ssl-cert-snakeoil.pem --ssl_private_key /etc/ssl/private/ssl-cert-snakeoil.key
"""  # noqa

from argparse import ArgumentParser, Namespace
import logging
# import errno
# import os
# import signal
# import time
# try:
#     import grp
#     import pwd
#     unix = True
# except ImportError:
#     grp = None
#     pwd = None
#     unix = False

import cherrypy
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import translation

from crate_anon.crateweb.config.wsgi import application as wsgi_application
# COULD ALSO USE:
#   from django.core.handlers.wsgi import WSGIHandler
#   wsgi_application = WSGIHandler()

log = logging.getLogger(__name__)


CRATE_STATIC_URL_PATH = settings.STATIC_URL.rstrip('/')
NEED_UNIX = "Need UNIX for group/user operations"
DEFAULT_ROOT = settings.FORCE_SCRIPT_NAME


class Command(BaseCommand):
    help = ("Run this project in a CherryPy webserver. To do this, "
            "CherryPy is required (pip install cherrypy).")

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            '--host', type=str, default="127.0.0.1",
            help="hostname to listen on (default: 127.0.0.1)")
        parser.add_argument(
            '--port', type=int, default=8088,
            help="port to listen on (default: 8088)")
        parser.add_argument(
            "--server_name", type=str, default="localhost",
            help="CherryPy's SERVER_NAME environ entry (default: localhost)")
        # parser.add_argument(
        #     "--daemonize", action="store_true",
        #     help="whether to detach from terminal (default: False)")
        # parser.add_argument(
        #     "--pidfile", type=str,
        #     help="write the spawned process ID to this file")
        # parser.add_argument(
        #     "--workdir", type=str,
        #     help="change to this directory when daemonizing")
        parser.add_argument(
            "--threads", type=int, default=10,
            help="Number of threads for server to use (default: 10)")
        parser.add_argument(
            "--ssl_certificate", type=str,
            help="SSL certificate file "
                 "(e.g. /etc/ssl/certs/ssl-cert-snakeoil.pem)")
        parser.add_argument(
            "--ssl_private_key", type=str,
            help="SSL private key file "
                 "(e.g. /etc/ssl/private/ssl-cert-snakeoil.key)")
        # parser.add_argument(
        #     "--server_user", type=str, default="www-data",
        #     help="user to run daemonized process (default: www-data)")
        # parser.add_argument(
        #     "--server_group", type=str, default="www-data",
        #     help="group to run daemonized process (default: www-data)")
        parser.add_argument(
            "--log_screen", dest="log_screen", action="store_true",
            help="log access requests etc. to terminal (default)")
        parser.add_argument(
            "--no_log_screen", dest="log_screen", action="store_false",
            help="don't log access requests etc. to terminal")
        parser.add_argument(
            "--debug_static", action="store_true",
            help="show debug info for static file requests")
        parser.add_argument(
            "--root_path", type=str, default=DEFAULT_ROOT,
            help="Root path to serve CRATE at. Default: {}".format(
                DEFAULT_ROOT))
        parser.set_defaults(log_screen=True)
        # parser.add_argument(
        #     "--stop", action="store_true",
        #     help="stop server")

    def handle(self, *args, **options):
        opts = Namespace(**options)
        # Activate the current language, because it won't get activated later.
        try:
            translation.activate(settings.LANGUAGE_CODE)
        except AttributeError:
            pass
        # noinspection PyTypeChecker
        runcpserver(opts)


# def change_uid_gid(uid, gid=None):
#     """Try to change UID and GID to the provided values.
#     UID and GID are given as names like 'nobody' not integer.
#
#     Src: http://mail.mems-exchange.org/durusmail/quixote-users/4940/1/
#     """
#     if not unix:
#         raise OSError(NEED_UNIX)
#     if not os.geteuid() == 0:
#         # Do not try to change the gid/uid if not root.
#         return
#     (uid, gid) = get_uid_gid(uid, gid)
#     os.setgid(gid)
#     os.setuid(uid)


# def get_uid_gid(uid, gid=None):
#     """Try to change UID and GID to the provided values.
#     UID and GID are given as names like 'nobody' not integer.
#
#     Src: http://mail.mems-exchange.org/durusmail/quixote-users/4940/1/
#     """
#     if not unix:
#         raise OSError(NEED_UNIX)
#     uid, default_grp = pwd.getpwnam(uid)[2:4]
#     if gid is None:
#         gid = default_grp
#     else:
#         try:
#             gid = grp.getgrnam(gid)[2]
#         except KeyError:
#             gid = default_grp
#     return uid, gid


# def still_alive(pid):
#     """
#     Poll for process with given pid up to 10 times waiting .25 seconds in
#     between each poll.
#     Returns False if the process no longer exists otherwise, True.
#     """
#     for n in range(10):
#         time.sleep(0.25)
#         try:
#             # poll the process state
#             os.kill(pid, 0)
#         except OSError as e:
#             if e[0] == errno.ESRCH:
#                 # process has died
#                 return False
#             else:
#                 raise  # TODO
#     return True


# def stop_server(pidfile):
#     """
#     Stop process whose pid was written to supplied pidfile.
#     First try SIGTERM and if it fails, SIGKILL.
#     If process is still running, an exception is raised.
#     """
#     if os.path.exists(pidfile):
#         pid = int(open(pidfile).read())
#         try:
#             os.kill(pid, signal.SIGTERM)
#         except OSError:  # process does not exist
#             os.remove(pidfile)
#             return
#         if still_alive(pid):
#             # process didn't exit cleanly, make one last effort to kill it
#             os.kill(pid, signal.SIGKILL)
#             if still_alive(pid):
#                 raise OSError("Process {} did not stop.".format(pid))
#         os.remove(pidfile)


class Missing(object):
    """Basic web interface to say "not here"."""
    config = {
        '/': {
            # Anything so as to prevent complaints about an empty config.
            'tools.sessions.on': False,
        }
    }

    @cherrypy.expose
    def index(self):
        return "[CherryPy server says:] Nothing to see here. Wrong URL path."


# noinspection PyUnresolvedReferences
def start_server(opts: Namespace) -> None:
    """
    Start CherryPy server
    """

    # if opts.daemonize and opts.server_user and opts.server_group:
    #     # ensure the that the daemon runs as specified user
    #     change_uid_gid(opts.server_user, opts.server_group)

    cherrypy.config.update({
        'server.socket_host': opts.host,
        'server.socket_port': opts.port,
        'server.thread_pool': opts.threads,
        'server.server_name': opts.server_name,
        'server.log_screen': opts.log_screen,
    })
    if opts.ssl_certificate and opts.ssl_private_key:
        cherrypy.config.update({
            'server.ssl_module': 'builtin',
            'server.ssl_certificate': opts.ssl_certificate,
            'server.ssl_private_key': opts.ssl_private_key,
        })

    log.info("Starting on host: {}".format(opts.host))
    log.info("Starting on port: {}".format(opts.port))
    log.info("Static files will be served from filesystem path: {}".format(
        settings.STATIC_ROOT))
    log.info("Static files will be served at URL path: {}".format(
        CRATE_STATIC_URL_PATH))
    log.info("CRATE will be at: {}".format(opts.root_path))
    log.info("Thread pool size: {}".format(opts.threads))

    static_config = {
        '/': {
            'tools.staticdir.root': settings.STATIC_ROOT,
            'tools.staticdir.debug': opts.debug_static,
        },
        CRATE_STATIC_URL_PATH: {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': '',
        },
    }
    cherrypy.tree.mount(Missing(), '', config=static_config)
    cherrypy.tree.graft(wsgi_application, opts.root_path)

    # noinspection PyBroadException,PyPep8
    try:
        cherrypy.engine.start()
        cherrypy.engine.block()
    except:  # 2017-03-13: shouldn't restrict to KeyboardInterrupt!
        cherrypy.engine.stop()


def runcpserver(opts: Namespace) -> None:
    # if opts.stop:
    #     if not opts.pidfile:
    #         raise ValueError("Must specify --pidfile to use --stop")
    #     print('stopping server')
    #     stop_server(opts.pidfile)
    #     return True

    # if opts.daemonize:
    #     if not opts.pidfile:
    #         opts.pidfile = '/var/run/cpserver_{}.pid'.format(opts.port)
    #     stop_server(opts.pidfile)
    #
    #     if opts.workdir:
    #         become_daemon(our_home_dir=opts.workdir)
    #     else:
    #         become_daemon()
    #
    #     fp = open(opts.pidfile, 'w')
    #     fp.write("{}\n".format(os.getpid()))
    #     fp.close()

    # Start the webserver
    log.info('starting server with options {}'.format(opts))
    start_server(opts)


def main():
    command = Command()
    parser = ArgumentParser()
    command.add_arguments(parser)
    cmdargs = parser.parse_args()
    runcpserver(cmdargs)


if __name__ == '__main__':
    main()
