==============
flask-rest-api
==============

.. image:: https://img.shields.io/travis/Nobatek/flask-rest-api/master.svg
        :target: https://travis-ci.org/Nobatek/flask-rest-api
        :alt: Build status

.. image:: https://coveralls.io/repos/github/Nobatek/flask-rest-api/badge.svg?branch=master
        :target: https://coveralls.io/github/Nobatek/flask-rest-api/?branch=master
        :alt: Code coverage

.. image:: https://api.codacy.com/project/badge/Grade/463485aeeac048f08cb4f40ebeb61160
        :target: https://www.codacy.com/app/lafrech/flask-rest-api
        :alt: Code health

Build a REST API with Flask and marshmallow.

**flask-rest-api** relies on `marshmallow <https://github.com/marshmallow-code/marshmallow>`_, `webargs <https://github.com/sloria/webargs>`_ and `apispec <https://github.com/marshmallow-code/apispec/>`_ to provide a complete REST API framework.

Features
========

- Serialization, deserialization and validation using marshmallow ``Schema``.
- OpenAPI (Swagger) specification automatically generated, and exposed with `ReDoc <https://github.com/Rebilly/ReDoc>`_.
- ETag.
- Pagination.

Install
=======

::

    pip install flask-rest-api

flask-rest-api supports Python >= 3.4.

License
=======

MIT licensed. See the `LICENSE <https://github.com/Nobatek/flask-rest-api/blob/master/LICENSE>`_ file for more details.


