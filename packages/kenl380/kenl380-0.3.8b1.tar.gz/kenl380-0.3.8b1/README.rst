kenl380 Package Repository
==========================

This is the top level package for the other python packages I have published on PyPI. It's function is basically to supply a namespace, so that I don't conflict with other modules and packages both on PyPI as well as in the site-packages directory for any given Python installation.

---------------

To see an example of a submodule that would be installed within this namespace, take a look at my ``pylib`` package, which you can find on GitHub `in this repository <https://github.com/kenlowrie/pylib>`_. When it is installed locally, it goes into the ``kenl380`` directory in site-packages, instead of into the root. When I import it, I normally do it like this:

``import kenl380.pylib as pylib``

That way I don't have to prefix the names with kenl380 everywhere...
