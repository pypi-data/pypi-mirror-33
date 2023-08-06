===================
Royal Mail Rest API
===================


.. image:: https://img.shields.io/pypi/v/royal_mail_rest_api.svg
        :target: https://pypi.python.org/pypi/royal_mail_rest_api

.. image:: https://api.travis-ci.org/Bobspadger/royal_mail_rest_api.svg
        :target: https://travis-ci.org/Bobspadger/royal_mail_rest_api

.. image:: https://readthedocs.org/projects/royal-mail-rest-api/badge/?version=latest
        :target: https://royal-mail-rest-api.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




A small helper for integrating python with Royal Mails Rest API

This is to help with getting started integrating Royal Mails shipping and Tracking API's into your project.

They do have an Open API to build this with Swagger-Codegen, but I found there were a few issues with this.
1. Horrible final code - overly verbose and complicated.
1. Half the time it would not build (needed beta versions of swagger-codegen) and then it would still not work.

This is cleaner, easier to modify and extend, and a lot lighter weight, only using the standard library.

It is VERY MUCH a work in progress, so help is hugely appreciated, and be careful, it may change as I implement more features / improve and enhance what we already have.



* Free software: MIT license
* Documentation: https://royal-mail-rest-api.readthedocs.io.


Features
--------

Create Labels
Update Labels
Create Manifests
Post Manifests


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
