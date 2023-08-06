dev-pipeline-bootstrap
======================
|codacy|
|code-climate|

A `dev-pipeline`_ plugin to add the :code:`bootstrap` command.
:code:`bootstrap` will update checkouts, then perform a build.  It's similar
but not quite identical to running :code:`checkout` and :code:`build` commands
(:code:`bootstrap` will interleave the operations).


Installation
------------
The simplest way to install is using pip_.

.. code:: bash

    $ cd /path/to/dev-pipeline-bootstrap
    $ pip3 install

If you don't have pip available, you can run :code:`setup.py` directly.

.. code:: bash

    $ cd /path/to/dev-pipeline-bootstrap
    $ python3 setup.py install

You'll need scm plugins installed to do anything useful.


Documentation
-------------
Information about the :code:`bootstrap` command is avaialble in the
documentation_.


.. |codacy| image:: https://api.codacy.com/project/badge/Grade/9521e63659524c70a1e8db68aa72a01f
    :target: https://www.codacy.com/app/snewell/dev-pipeline-bootstrap?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=dev-pipeline/dev-pipeline-bootstrap&amp;utm_campaign=Badge_Grade

.. |code-climate| image:: https://api.codeclimate.com/v1/badges/3a5232de060ffe316d1e/maintainability
   :target: https://codeclimate.com/github/dev-pipeline/dev-pipeline-bootstrap/maintainability
   :alt: Maintainability

.. _dev-pipeline: https://github.com/dev-pipeline/dev-pipeline
.. _documentation: docs/command-bootstrap.rst
.. _pip: https://pypi.python.org/pypi/pip


