***********************************
Rigado Sphinx Themes and Extensions
***********************************

Usage
=====

``pip install sphinx-rigado-theme``

Developing & Publishing
=======================

Setup user account on PyPI: https://packaging.python.org/tutorials/packaging-projects/

To publish:

1. make sure version is ok in ``sphinx_rigado_theme/__init__.py``
2. ``python3 setup.py sdist bdist_wheel``
3. ``twine upload dist/sphinx_rigado_theme-0.0.3*``
