nose-template-usage
===================

A Nose plugin that displays which Django and/or Pyramid Chameleon ZPT templates were and were not used
(loaded) during test execution.

Installation
------------
*only django usage is available on pip*
::

    pip install nose-template-usage

Usage
-----

Django
    To enable the template usage report, include the ``--with-django-template-usage-report``
    command line option when running your tests with ``python setup.py nosetests``
    or the ``nosetests`` command.

Pyramid
    To enable the template usage report, include the ``--with-pyramid-template-usage-report``
    command line option when running your tests with ``python setup.py nosetests``
    or the ``nosetests`` command.

    To list the unused templates you must provide the ``--pyramid-template-match=unix*wildcard*match``.
    Since Pyramid looks for templates anywhere you want it to.

    The plugin finds usage based on calls to ``pyramid.chameleon_zpt.ZPTTemplateRenderer`` which
    is the default Pyramid template renderer.

Ignoring Directories
~~~~~~~~~~~~~~~~~~~~
*not yet tested with pyramid*

You probably don't want to include templates from third-party libraries in your
template usage report. To ignore template prefixes, use the
``--ignore-template-prefix=path/`` option. The value of the ``path/`` is the
path relative to the template loader.
