===================
TargetGeneIntersect
===================


.. image:: https://img.shields.io/pypi/v/targeneintersect.svg
        :target: https://pypi.python.org/pypi/targeneintersect

.. image:: https://img.shields.io/travis/isabelleberger/targeneintersect.svg
        :target: https://travis-ci.org/isabelleberger/targeneintersect

.. image:: https://readthedocs.org/projects/targeneintersect/badge/?version=latest
        :target: https://targeneintersect.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/isabelleberger/targeneintersect/shield.svg
     :target: https://pyup.io/repos/github/isabelleberger/targeneintersect/
     :alt: Updates



A baby package that uses `pybedtools <https://github.com/daler/pybedtools>`_ intersect to gain target gene names for genomic data in a pandas dataframe. My first attempt at packaging, as well as a useful little tool for something I end up copying and pasting all the time.

* Free software: MIT license
* Documentation: https://targeneintersect.readthedocs.io.


Features
--------

* Input a BED formatted gene file and a BED formatted dataframe of genomic data
* Receive a dataframe that now includes target gene names

Credits
-------

This package is based on the `BEDTools <https://github.com/arq5x/bedtools2>`_ function intersect, as implemented in python by `pybedtools <https://github.com/daler/pybedtools>`_. This package was created with `Cookiecutter <https://github.com/audreyr/cookiecutter>`_ and the `audreyr/cookiecutter-pypackage <https://github.com/audreyr/cookiecutter-pypackage>`_ project template.
