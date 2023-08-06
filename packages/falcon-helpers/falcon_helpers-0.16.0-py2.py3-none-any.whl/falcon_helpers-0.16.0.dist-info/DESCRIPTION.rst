.. default-role:: code
.. role:: python(code)
  :language: python


.. image:: https://codecov.io/gl/skosh/falcon-helpers/branch/master/graph/badge.svg
  :target: https://codecov.io/gl/skosh/falcon-helpers

.. image:: https://gitlab.com/skosh/falcon-helpers/badges/master/pipeline.svg
  :target: https://gitlab.com/skosh/falcon-helpers/commits/master


==============
Falcon Helpers
==============

A number of helpful utilities to make working with Falcon Framework a breeze.


Quickstart
----------

.. code:: sh

  $ pip install falcon-helpers


.. code::

  import falcon
  import falcon_helpers

  api = falcon.API(
    middlewares=[
      falcon_helpers.middlewares.StaticsMiddleware()
    ]
  )


0.16.0 - 2018-06-25
###################

* [FEAT] Create a New Base API Implementation (ed3f715_)
* [BUG] Squash a bunch of bugs

.. _ed3f715: https://gitlab.com/skosh/falcon-helpers/commit/ed3f715


0.15.3 - 2018-06-18
###################

* [FEAT] Fetching a file pointer in storage allows you to set the mode.


0.15.2 - 2018-06-06
###################

* [FEAT]  Support passing S3 configuration to storages
* [BREAK] Default to using V4 of the AWS presigned key


0.15.1 - 2018-06-06
###################

* [FEAT] Allow column_filters to use non-entity columns


0.15.0 - 2018-06-02
###################

* [FEAT] Add Support for easier PUT updates (31d6175_)

.. _31d6175: https://gitlab.com/skosh/falcon-helpers/commit/31d6175


0.14.0 - 2018-06-01
###################

* [BREAK] Remove Statics Middleware
* [NEW] Add a simple Sentry Plugin
* [NEW] Create a server CLI


0.13.0 - 2018-05-22
###################

* [BREAK] SQLAlchemy Session is now a global (9d5d220_)
* [FEAT] Implement fetching from storage environments (7f7fc01_)
* [NEW] Add a basic Mapping type for Configuration objects (1884577_)
* [BUG] Allow None for Storage Paths (e3b625d_)

.. _9d5d220: https://gitlab.com/skosh/falcon-helpers/commit/9d5d220
.. _7f7fc01: https://gitlab.com/skosh/falcon-helpers/commit/7f7fc01
.. _1884577: https://gitlab.com/skosh/falcon-helpers/commit/1884577
.. _e3b625d: https://gitlab.com/skosh/falcon-helpers/commit/e3b625d


0.12.0 - 2018-04-15
###################

* [FEAT] Create Key Based Filtering


0.11.4 - 2018-04-05
###################

* [FEAT] Allow specifying your own default page size for ListBase


0.11.3 - 2018-03-31
###################

* [FEAT] Allow passing additional data to generate auth token

0.11.2 - 2018-03-30
###################

* [BUG] Remove Stray PDB

0.11.1 - 2018-03-30
###################

* [FEAT] Add hook to for deleting an object in CrudBase


0.11.0 - 2018-03-29
###################

* [FEAT] Add filter by field name on ListBase
* [FEAT] Allow turning off auto-marshalling
* [BUG] Session closing could fail with exceptions


0.10.1 - 2018-03-05
###################

* [FEAT] Added a remove function to storage backends


0.10.0 - 2018-03-03
###################

* [NEW] We now have a CI system with CodeCoverage
* [FEAT] You can now user auth_marshal=False to turn off auto JSON marshaling to Marshmallow
* [FEAT] Added a few helpful functions on auth.user
* [BUG] Fixed object deletion of CrudBase (which was what kicked the CI setup into high-gear)


0.9.6 - 2018-03-02
##################

* [BUG] Forgot a self

0.9.5 - 2018-03-01
##################

* [NEW] get_object was implemented for CrudBase
* [FEAT] has_permission now supports an enum type
* [NEW] kwargs is now used on CrudBase


0.9.3 - 2018-02-28
##################

* [BUG] Fix an issue with binary file opening
* [BUG] Utilize the correct exception with CRUD Base


0.9.2 - 2018-02-27
##################

[CHANGE] Add in fuzzy testing for nullable ORM columns


0.9.1 - 2018-02-24
##################
* [BUG] Add the Falcon-Multipart Requirement


0.9.0 - 2018-02-23
##################

* [FEAT] Added Support to Downloading
* [CHANGE] Renamed contrib.upload to contrib.storage


0.8.0 - 2018-02-23
##################

* [NEW] Add a Basic File Storage System (7c0bd4b_)
* [FEAT] CRUD resources now support \*\*kwargs (1d4543_)

.. _7c0bd4b: https://gitlab.com/skosh/falcon-helpers/commit/7c0bd4b
.. _1d4543: https://gitlab.com/skosh/falcon-helpers/commit/1d4543


0.7.0 - 2018-02-15
##################

** [NEW] Added a CRUD Base Library
** [FEAT] Added a token generation method to the user
** [CHANGE] Cleaned up the REPR for permissions entity
** [CHANGE] Only close the SA session when failure occurs
** [FIX] auth_required accepts the proper arguments


0.6.1 - 2017-12-15
##################

** [BUG] Add a req/resp to failed action functions
** [FEAT] Make ParseJWTMiddleware available at the middleware level
** [BUG] Allow setting of the get_id function


0.6.0 - 2017-12-15
##################

** [NEW] Added a global SQLAlchemy Scoped Session to facilitate testing and other items
** [CHANGE] AuthRequiredMiddleware was split into two and there is a new ParseJWTMiddleware
** [BUG] Cleaned up a number of issues with the way SQLAlchemy ORM is being used


0.5.0 - 2017-12-02
##################

+* [NEW]  A brand-spanking new permission system with users, groups, and permissions
+* [FEAT] Post-login redirect is now configurable.
+* [FEAT] Create a simple redirection resource
+* [FEAT] Jinja2 Middleware can take application globals to inject into the template
+* [FEAT] Added a mixin for testing entities

0.4.2 - 2017-10-25
==================
* Enable Auth Middleware to always run. Helpful when then entire application is
  an API that requires authentication.

0.4.1 - 2017-10-19
==================

* Fix issue with importing Marshmallow Middleware

0.4.0 - 2017-10-14
==================

* Added Marshmallow Middleware for auto schema loading (655cf76_)

.. _655cf76: https://gitlab.com/skosh/falcon-helpers/commit/655cf76


0.3.1 - 2017-10-09
==================

* [FEAT] Add a number of helpful SQLAlchemy Features

0.3.0 - 2017-10-07
==================

* [FEAT] Setup SQLAlchemy
* [BUG] Install cryptography for JWT's with RSA algo

0.2.1 - 2017-10-07
==================
* Fix issue when using HS256 tokens for authentication

0.2.0 - 2017-09-23
==================
* Release the Package and update the source location

0.1.0 - 2017-08-22
==================

* Added StaticsMiddleware


