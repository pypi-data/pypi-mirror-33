A Bugzilla plugin for helga chat bot
====================================

.. image:: https://travis-ci.org/ktdreyer/helga-bugzilla.svg?branch=master
       :target: https://travis-ci.org/ktdreyer/helga-bugzilla

.. image:: https://badge.fury.io/py/helga-bugzilla.svg
       :target: https://badge.fury.io/py/helga-bugzilla

About
-----

Helga is a Python chat bot. Full documentation can be found at
http://helga.readthedocs.org.

This Bugzilla plugin allows Helga to respond to Bugzilla ticket numbers in IRC
and print information about the tickets. For example::

  03:14 < ktdreyer> bz 1217809
  03:14 < helgabot> ktdreyer might be talking about
                    https://bugzilla.redhat.com/1217809
                    [[TRACKER] SELinux support]

The bot can also search external trackers. This allows you to find BZs for
other systems' tickets. For example::

  03:14 < ktdreyer> what bz is http://tracker.ceph.com/issues/16673 ?
  03:14 < helgabot> ktdreyer, http://tracker.ceph.com/issues/16673 is
                    https://bugzilla.redhat.com/1422893 [[RFE] rgw: add suport
                    for Swift-at-root dependent features of Swift API]

This uses a `Red Hat Bugzilla extension <https://bugzilla.redhat.com/docs/en/html/api/extensions/ExternalBugs/lib/WebService.html>`_.

Installation
------------
This Bugzilla plugin is `available from PyPI
<https://pypi.python.org/pypi/helga-bugzilla>`_, so you can simply install it
with ``pip``::

  pip install helga-bugzilla

If you want to hack on the helga-bugzilla source code, in your virtualenv where
you are running Helga, clone a copy of this repository from GitHub and run
``python setup.py develop``.

Optional: URL Configuration
---------------------------

In your ``settings.py`` file (or whatever you pass to ``helga --settings``),
you can specify a ``BUGZILLA_XMLRPC_URL``. For example::

  BUGZILLA_XMLRPC_URL = 'https://bugzilla.redhat.com/xmlrpc.cgi'

(If you do not specify this setting, the plugin will use txbugzilla's default
URL, which is Red Hat's bugzilla.)

You can also specify a URL format::

  BUGZILLA_TICKET_URL = "https://bugzilla.redhat.com/%(ticket)s"

The ``%(ticket)s`` format string will be replaced with the bug number.
Since the underlying library (txbugzilla) already constructs these web
URLs for bugs automatically, you probably don't need to add this setting
to helga. It's only necessary if your custom Bugzilla requires some
other URL scheme.

Optional: Authenticated access
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, Helga only reads tickets that are publicly accessible. You may
optionally give Helga privileged access to Bugzilla and allow Helga to read
private bugs by setting up a `python-bugzilla
<https://pypi.python.org/pypi/python-bugzilla>`_ credential::

  $ pip install python-bugzilla
  $ bugzilla login
  (enter your username and password)

(Use ``bugzilla --bugzilla=https://bugzilla.example.com/xmlrpc.cgi login``
here if the XMLRPC URI is not the default,
https://bugzilla.redhat.com/xmlrpc.cgi)

This ``bugzilla login`` command will save your login credential to
``.bugzillatoken``. When this is set, Helga will be able to read private bugs
with using the permissions of the user to whom the API key belongs.

**Note**: This authentication feature can expose private information (ticket
subjects) about your Bugzilla bugs. If you use this feature, be sure that the
networks to which Helga connects are restricted. Everyone in Helga's channels
will see the private information, so the assumption is that they already have
rights to read the private bugs.
