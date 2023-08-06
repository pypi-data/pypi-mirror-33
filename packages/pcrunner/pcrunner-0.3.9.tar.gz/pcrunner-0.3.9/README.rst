========
Pcrunner
========


.. image:: https://img.shields.io/pypi/v/pcrunner.svg
        :target: https://pypi.python.org/pypi/pcrunner
        :alt: pypi

.. image:: https://img.shields.io/travis/maartenq/pcrunner.svg
        :target: https://travis-ci.org/maartenq/pcrunner
        :alt: build

.. image:: https://readthedocs.org/projects/pcrunner/badge/?version=latest
        :target: https://pcrunner.readthedocs.io/en/latest/?badge=latest
        :alt: docs

.. image:: https://pyup.io/repos/github/maartenq/pcrunner/shield.svg
        :target: https://pyup.io/repos/github/maartenq/pcrunner/
        :alt: pyup

.. image:: https://codecov.io/gh/maartenq/pcrunner/branch/master/graph/badge.svg
        :target: https://codecov.io/gh/maartenq/pcrunner
        :alt: codecov

Pcrunner (Passive Checks Runner is a daemon and service that periodically runs
Nagios_ / Icinga_ checks paralell. The results are posted via HTTPS to a
`NSCAweb`_ server.

* GitHub: https://github.com/maartenq/pcrunner
* Free software: https://opensource.org/licenses/ISC
* PyPi: https://pypi.python.org/pypi/pcrunner
* Documentation: https://pcrunner.readthedocs.io/en/latest/
* Travis CI: https://travis-ci.org/maartenq/pcrunner
* Codecov: https://codecov.io/github/maartenq/pcrunner


Features
--------

* Runs as a daemon on Linux.
* Runs as a service on win32.
* Command line interface for single test runs and/or cron use.
* Parallel execution of check commands.
* Posts check results external commands.
* Termniation of check commands if maximum time exceeds.
* Configuration in YAML.
* Command definition in YAML or text format.


Credits
-------

This package was created with Cookiecutter_ and the
`audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _NSCAweb: https://github.com/smetj/nscaweb
.. _Nagios: https://www.nagios.org/
.. _Icinga: https://www.icinga.org/
