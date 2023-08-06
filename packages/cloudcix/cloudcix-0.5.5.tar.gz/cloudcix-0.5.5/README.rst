Overview
========

``cloudcix`` is a Python client for the CloudCIX REST API for rapidly
building secure, scalable CloudCIX applications.

For more information about CloudCIX, see
`here <http://www.cix.ie/#/services/saas>`__.

Installation
------------

Prerequisites
~~~~~~~~~~~~~

1. Create an account on the CloudCIX Platform

   -  `Register <https://auth.cloudcix.com/register>`__

2. Retrieve your API Key

   -  Under the ``My Membership`` tab in the sidebar, click on
      ``Member Details``
   -  The ``API Key`` should be available at the top of the form

3. Ensure that you have both Python and pip installed

   -  As of right now, the ``cloudcix`` module is available at different
      versions for Python2 and Python3
   -  We recommend you use Python3 and the latest version of the
      ``cloudcix`` module
   -  `Python <http://docs.python-guide.org/en/latest/starting/installation/>`__
   -  `pip <https://pip.pypa.io/en/stable/installing/>`__

Installing the ``cloudcix`` library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The cloudcix library is installed using the ``pip`` module.

Depending on your version of Python, you need to install different
versions of ``cloudcix``

-  Python3

   -  ``pip3 install -U cloudcix``

-  Python2

   -  ``pip install -U 'cloudcix<0.3'``

The 0.2 releases are the last to support Python2. If you still use
Python2 we recommend you upgrade to Python3 as support will be dropped
for these versions in time.

Required settings
~~~~~~~~~~~~~~~~~

In order to run a project, the module requires some setting variables to
exist.

The variables required are as follows:

-  ``CLOUDCIX_API_URL``

   -  The base url of the api
   -  Usually ``https://api.cloudcix.com/`` but could change over time

-  ``CLOUDCIX_AUTH_URL``

   -  The base url of the auth server
   -  Usually ``https://keystone.cloudcix.com:5000/v3/`` but could
      change over time

-  ``CLOUDCIX_API_USERNAME``

   -  The email of the account that you signed up with

-  ``CLOUDCIX_API_PASSWORD``

   -  The password associated with your CloudCIX account

-  ``CLOUDCIX_API_KEY``

   -  The API key associated with your CloudCIX Member (see
      **Prerequisites**)

These variables can be declared in a settings file, as follows

.. code:: python

    # In main python script
    import os
    os.environ.setdefault("CLOUDCIX_SETTINGS_MODULE", "my_project.my_settings")

.. code:: python

    # In my_project/my_settings.py
    CLOUDCIX_API_URL = 'https://api.cloudcix.com'
    CLOUDCIX_API_USERNAME = 'EMAIL'               # CloudCIX login
    CLOUDCIX_API_PASSWORD = 'PASSWORD'            # CloudCIX password
    CLOUDCIX_API_KEY = 'NUMBER/CHARACTER STRING'  # CloudCIX api key
    CLOUDCIX_AUTH_URL = 'https://keystone.cloudcix.com:5000/v3'

Small Example
-------------

**Pull a list of Countries from the CloudCIX API** *Assume the above
settings file is available*

.. code:: python

    import os

    os.environ.setdefault("CLOUDCIX_SETTINGS_MODULE", "my_project.my_settings")

    # NOTE: environ variables must be set before importing cloudcix

    from cloudcix import api

    # Get a util function to get a session using the credentials in your settings file
    from cloudcix.utils import get_admin_session

    # Get your authentication token for your login
    token = get_admin_session().get_token()
    # Get a list of the countries from the Membership Application passing your token for authentication
    response = api.membership.country.list(token=token)

    # Print out the json of the response data
    print(response.json())

More Examples
-------------

For more examples, see the examples file
