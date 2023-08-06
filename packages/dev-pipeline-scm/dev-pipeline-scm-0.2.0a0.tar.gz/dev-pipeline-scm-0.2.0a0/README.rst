dev-pipeline-scm
================
|codacy|
|code-climate|

A `dev-pipeline`_ plugin to provide source control functionality.  It will add
the :code:`checkout` command to :code:`dev-pipeline`, permitting use of any
installed scm plugin.


Installation
------------
The simplest way to install is using pip_.

.. code:: bash

    $ cd /path/to/dev-pipeline-scm
    $ pip3 install

If you don't have pip available, you can run :code:`setup.py` directly.

.. code:: bash

    $ cd /path/to/dev-pipeline-scm
    $ python3 setup.py install

You'll need scm plugins installed to do anything useful.


Documentation
-------------
Information about the :code:`checkout` command is avaialble in the
documentation_.


.. |codacy| image:: https://api.codacy.com/project/badge/Grade/dd2e50667c5c41e68f4a3fbfc33a4b0f
    :target: https://www.codacy.com/app/snewell/dev-pipeline-scm?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=dev-pipeline/dev-pipeline-scm&amp;utm_campaign=Badge_Grade

.. |code-climate| image:: https://api.codeclimate.com/v1/badges/35f2d6e196a7470d9be6/maintainability
   :target: https://codeclimate.com/github/dev-pipeline/dev-pipeline-scm/maintainability
   :alt: Maintainability

.. _dev-pipeline: https://github.com/dev-pipeline/dev-pipeline
.. _documentation: docs/command-checkout.rst
.. _pip: https://pypi.python.org/pypi/pip
