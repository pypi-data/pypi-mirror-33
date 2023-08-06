python-social-auth-wykop
===========================

Pluggable authentication backend for python-social-auth, that allows authentication via [https://wykop.pl/](https://wykop.pl).


## Installation instructions

From pypi

    $ pip install social-auth-wykop

or clone from Github

    $ git clone git@github.com:noisy/python-social-auth-wykop.git
    $ cd python-social-auth-wykop && sudo python setup.py install

## Pre-requisites

`python-social-auth` must be installed and configured first. Please visit the
[python-social-auth documentation](http://python-social-auth-docs.readthedocs.io/) for instructions.


## Configuration instructions

1. Add `WykopAPIv1` backend to AUTHENTICATION_BACKENDS:

        AUTHENTICATION_BACKENDS = (
            'social_auth_wykop.backends.WykopAPIv1',
            ...
            'django.contrib.auth.backends.ModelBackend',
        )

2. Add your Wykop settings to your django `settings.py` file.

        SOCIAL_AUTH_WYKOP_KEY = '...'
        SOCIAL_AUTH_WYKOP_SECRET = '...'

## Examples

Ready to use examples of projects in Django, Flask and Tornado frameworks are prepared here:

https://github.com/noisy/python-social-auth-wykop-examples

## Changelog

### 0.0.2
* changes in structure of directories

### 0.0.1
* Initial release

