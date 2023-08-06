﻿ibmcloudenv
===========

.. image:: https://travis.ibm.com/arf/IBM-Cloud-Env.svg?token=n4pCcFL1DYKbYcWx28RG&branch=development
    :target: https://travis.ibm.com/arf/IBM-Cloud-Env

`Available on PyPI <https://pypi.python.org/pypi/ibmcloudenv>`_

This library is the Python version of the the `JavaScript IBMCloudEnv library <https://github.com/ibm-developer/ibm-cloud-env>`_

The ``ibmcloudenv`` package allows to abstract environment variables
from various Cloud compute providers, such as, but not limited to,
CloudFoundry and Kubernetes, so the application could be
environment-agnostic.
The module allows to define an array of search patterns that will be
executed one by one until required value is found.

Installation
~~~~~~~~~~~~

.. code:: bash

    pip install ibmcloudenv

Usage
~~~~~

Create a JSON file containing your mappings and initialize the module

.. code:: python

    from ibmcloudenv import IBMCloudEnv
    IBMCloudEnv.init("/path/to/the/mappings/file/relative/to/prject/root")

In case mappings file path is not specified in the
``IBMCloudEnv.init()`` the module will try to load mappings from a
default path of ``/server/config/mappings.json``.

Supported search patterns types
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ibm\_cloud\_config supports searching for values using three search
pattern types - cloudfoundry, env, file.

-  Using ``cloudfoundry`` allows to search for values in VCAP\_SERVICES
   and VCAP\_APPLICATIONS environment variables
-  Using ``env`` allows to search for values in environment variables
-  Using ``file`` allows to search for values in text/json files

Example search patterns
^^^^^^^^^^^^^^^^^^^^^^^

-  cloudfoundry:service-instance-name - searches through parsed
   VCAP\_SERVICES environment variable and returns the ``credentials``
   object of the matching service instance name
-  cloudfoundry:$.JSONPath - searches through parsed VCAP\_SERVICES and
   VCAP\_APPLICATION environment variables and returns the value that
   corresponds to JSONPath
-  env:env-var-name - returns environment variable named “env-var-name”
-  env:env-var-name:$.JSONPath - attempts to parse the environment
   variable “env-var-name” and return a value that corresponds to
   JSONPath
-  file:/server/config.text - returns content of /server/config.text
   file
-  file:/server/config.json:$.JSONPath - reads the content of
   /server/config.json file, tries to parse it, returns the value that
   corresponds to JSONPath

mappings.json file example
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: javascript

    {
        "service1-credentials": {
            "searchPatterns": [
                "user-provided:my-service1-instance-name:username",
                "cloudfoundry:my-service1-instance-name",
                "env:my-service1-credentials",
                "file:/localdev/my-service1-credentials.json"
            ]
        },
        "service2-credentials": {
            "searchPatterns":[
                "user-provided:my-service1-instance-name:username",
                "cloudfoundry:$.service2[@.name=='my-service2-instance-name'].credentials.username",
                "env:my-service2-credentials:$.username",
                "file:/localdev/my-service1-credentials.json:$.username"
            ]
        }
    }

mappings.json version 2 file example

.. code:: javascript

    {   "version": 2,
        "my-service1": {
            "name": {
                    "searchPatterns": [
                    "cloudfoundry:my-service1-instance-name",
                    "env:my-service1-credentials",
                    "file:/localdev/my-service1-credentials.json"
                ]
            }
        },
        "my-service2": {
            "name": {
                "searchPatterns":[
                    "user-provided:service2-credentials-name:username",
                    "cloudfoundry:$.service2[@.name=='my-service2-instance-name'].credentials.username",
                    "env:my-service2-credentials:$.username",
                    "file:/localdev/my-service1-credentials.json:$.username"
                ]
            }
        }
    }


Using the values in application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In your application retrieve the values using below commands

.. code:: python

    service1credentials = IBMCloudEnv.getDictionary("service1-credentials") # this will be a dictionary
    service2username = IBMCloudEnv.getString("service2-username") # this will be a string



Contributions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Do a pull request against master, make sure the build passes. A team member will review and merge your pull request. Once merged to master, the version will be auto-incremented and published.

Make sure that your commit contains **fix** for *patch* changes **feat** for *minor* changes and **BREAKING CHANGE** for *major* changes. **BREAKING CHANGE** should be reflectede in the
body of the message

*Example of versions to upgrade types*

    1.0.0 -- 1.0.1 => patch / fix
    1.0.0 -- 1.1.0 => minor / feat
    1.0.0 -- 2.0.0 => major / BREAKING CHANGE

*Example of commit body*

    <type>(<scope>): <subject>

    <BLANK LINE>

    <body>

    <BLANK LINE>

<footer>

**Note:** scope, body, and footer are optional

*Example shown below*

    fix(docs) - fixed spelling error

For more information on the commit convention visit `Conventional Commits <https://conventionalcommits.org>`_

Deprecation Note
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`ibm_cloud_env <https://pypi.python.org/pypi/ibm_cloud_env/0.0.2>`_ is deprecated use ``ibmcloudenv``.
