****************
xld-py-cli
****************

Python CLI for `XL Deploy`_.
For more information, see the documentation_.

.. _XL Deploy: https://xebialabs.com/products/xl-deploy
.. _documentation: https://docs.xebialabs.com/xl-deploy/concept/xl-deploy-lightweight-cli.html

Usage
=======
::

    $ xld --url URL --username USERNAME --password PASSWORD apply FILENAME

    $ xld --url URL --username USERNAME --password PASSWORD generate DIRECTORIES

    $ xld --url URL --username USERNAME --password PASSWORD deploy VERSION ENVIRONMENT

Add `--debug` to see the stacktrace

    $ xld --url URL --username USERNAME --password PASSWORD apply FILENAME --debug

    $ xld --url URL --username USERNAME --password PASSWORD generate DIRECTORIES --debug

    $ xld --url URL --username USERNAME --password PASSWORD deploy VERSION ENVIRONMENT --debug

Installation
============
::

    $ pip install xld-py-cli

Testing
============
On xl-deploy base folder

    $ ./gradle pytest
