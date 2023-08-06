dev-pipeline-build-order
========================
|codacy|
|code-climate|

A `dev-pipeline`_ plugin to add the :code:`build-order` command.
:code:`build-order` will provide information about the order components will be
built in various output formats.


Installation
------------
The simplest way to install is using pip_.

.. code:: bash

    $ cd /path/to/dev-pipeline-build-order
    $ pip3 install

If you don't have pip available, you can run :code:`setup.py` directly.

.. code:: bash

    $ cd /path/to/dev-pipeline-build-order
    $ python3 setup.py install

You'll need scm plugins installed to do anything useful.


Documentation
-------------
Information about the :code:`build-order` command is avaialble in the
documentation_.


.. |codacy| image:: https://api.codacy.com/project/badge/Grade/1d9c1b2a684c43c3acd92173b1ec4b37
    :target: https://www.codacy.com/app/snewell/dev-pipeline-build-order?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=dev-pipeline/dev-pipeline-build-order&amp;utm_campaign=Badge_Grade

.. |code-climate| image:: https://api.codeclimate.com/v1/badges/929fecef0e6a0ca9e639/maintainability
   :target: https://codeclimate.com/github/dev-pipeline/dev-pipeline-build-order/maintainability
   :alt: Maintainability

.. _dev-pipeline: https://github.com/dev-pipeline/dev-pipeline
.. _documentation: docs/command-build-order.rst
.. _pip: https://pypi.python.org/pypi/pip
