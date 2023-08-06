sleek-lvalert Documentation
============================

sleek-lvalert is a client for the LIGO/Virgo LVAlert pubsub infrastructure that
is powered by SleekXMPP_. It is compatible with Python 3.

Quick Start
-----------

Install with pip_::

    pip install sleek-lvalert

Put your username and password in your netrc_ file in ``~/.netrc``::

    echo 'machine lvalert-test.cgca.uwm.edu login albert.einstein password gravity' >> ~/.netrc
    chmod 0600 ~/.netrc

Subscribe to some nodes::

    lvalert subscribe cbc_gstlal cbc_pycbc cbc_mbtaonline

Listen for LVAlert messages::

    lvalert listen

API
---

.. automodule:: sleek_lvalert

Command Line Interface
----------------------

.. argparse::
    :module: sleek_lvalert.tool
    :func: parser

.. _netrc: https://www.gnu.org/software/inetutils/manual/html_node/The-_002enetrc-file.html
.. _SleekXMPP: http://sleekxmpp.com
.. _pip: http://pip.pypa.io