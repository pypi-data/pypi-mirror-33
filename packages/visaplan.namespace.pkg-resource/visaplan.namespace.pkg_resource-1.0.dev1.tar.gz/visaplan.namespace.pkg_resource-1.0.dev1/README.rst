.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

===============================
visaplan.namespace.pkg_resource
===============================

This is a dummy package which does nothing except providing the `visaplan`
package and namespace package, "pkg_resource style";
it is a workaround for the problem of e.g. `visaplan.tools` being installable,
but under certain circumstances, the package namespace doesn't work, and the
visaplan.tools submodules cannot be accessed from the buildout-generated Plone
instance (see <https://community.plone.org/t/factoring-out-packages-namespace-problem/6842>).

Once this problem is solved, the `visaplan.namespace.pkg_resource` package will be obsolete.


Features
--------

- Provides an empty namespace package `visaplan`.


Installation
------------

Install the `visaplan` dummy package by adding it to your buildout::

    [buildout]

    ...

    eggs =
        visaplan.namespace.pkg_resource
        visaplan.tools
        ...


and then running ``bin/buildout``


Contribute
----------

- Issue Tracker: https://github.com/visaplan/visaplan.namespace.pkg_resource/issues
- Source Code: https://github.com/visaplan/visaplan.namespace.pkg_resource


Support
-------

If you are having issues, please let us know;
please use the issue tracker mentioned above.


License
-------

The project is available under the Apache License 2.0 or the GNU GPL 2.0
