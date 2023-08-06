=============================
django-rest-kakao-auto-reply
=============================

.. image:: https://badge.fury.io/py/django-rest-kakao-auto-reply.svg
    :target: https://badge.fury.io/py/django-rest-kakao-auto-reply

.. image:: https://travis-ci.org/iamchanii/django-rest-kakao-auto-reply.svg?branch=master
    :target: https://travis-ci.org/iamchanii/django-rest-kakao-auto-reply

.. image:: https://codecov.io/gh/iamchanii/django-rest-kakao-auto-reply/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/iamchanii/django-rest-kakao-auto-reply

Your project description goes here

Documentation
-------------

The full documentation is at https://django-rest-kakao-auto-reply.readthedocs.io.

Quickstart
----------

Install django-rest-kakao-auto-reply::

    pip install django-rest-kakao-auto-reply

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'kakao_auto_reply.apps.KakaoAutoReplyConfig',
        ...
    )

Add django-rest-kakao-auto-reply's URL patterns:

.. code-block:: python

    from kakao_auto_reply import urls as kakao_auto_reply_urls


    urlpatterns = [
        ...
        url(r'^', include(kakao_auto_reply_urls)),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
