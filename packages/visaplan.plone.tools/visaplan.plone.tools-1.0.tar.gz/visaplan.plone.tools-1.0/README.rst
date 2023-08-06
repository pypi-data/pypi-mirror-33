.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

====================
visaplan.plone.tools
====================

General tools modules for Plone

Features
--------

Modules in version 1.0:

- "context" module

  Several tools for processing the request.
  Some need some modernization ...

- "cfg" module

  Read "product" configuration, and detect development mode

- "log" module

  Automatically named loggers

- "functions" module

  Some functions, e.g. "is_uid_shaped"


Documentation
-------------

The modules are documented by doctests.
Full documentation for end users can be found in the "docs" folder.


Translations
------------

This product has been translated into

- Klingon (thanks, K'Plai)


Installation
------------

Since visaplan.plone.tools is a package for Plone instances,
it is not normally installed using pip;
instead, install it by adding it to your buildout::

    [buildout]

    ...

    eggs =
        visaplan.plone.tools


and then running ``bin/buildout``


Contribute
----------

- Issue Tracker: https://github.com/visaplan/visaplan.UnitraccShop/issues
- Source Code: https://github.com/visaplan/visaplan.plone.tools
- Documentation: https://docs.plone.org/foo/bar


Support
-------

If you are having issues, please let us know;
please use the issue tracker mentioned above.


License
-------

The project is licensed under the Apache Software License.
