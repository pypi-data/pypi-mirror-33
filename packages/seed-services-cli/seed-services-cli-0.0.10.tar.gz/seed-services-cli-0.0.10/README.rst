Seed Services command line interface
====================================

A command line interface for `Seed Services`_ HTTP APIs.

.. _Seed Services: https://github.com/praekelt?utf8=%E2%9C%93&query=seed


Installation
------------

Install with::

  $ pip install --user seed-services-cli (--user option may not be necessary when running a virtual environment)

Then run::

  $ seed-services-cli --help

and read the usage instructions.


Configuration
----------------

The configuration can be passed in using a YAML file. An example is provided::

  hub:
    api_url: http://hub.example.org/api/v1
    token: TEMP
  identity_store:
    api_url: http://idstore.example.org/api/v1
    token: TEMP2

Then run the following to use::

  $ seed-services-cli --conf=config.yaml command-to-run



Finding identities
------------------

Run::

  $ seed-services-cli identity-search --help

to learn about the options available for searching.

Example search::

  $ seed-services-cli identity-search --address_type msisdn --address +27001


Get identity details
--------------------

Run::

  $ seed-services-cli identity-get --identity uuid

to get a specific identity details dump to json


Identities Upload
---------------------------

Run::

  $ seed-services-cli identity-import --help

to learn about the identity upload instructions.

Then to upload content create a CSV or JSON file ::

  $ seed-services-cli identity-import --csv filename.csv

Find demo_import_identities.csv and .json in the repo route for format example.

Identities Details Update
-------------------------

This command is used to update the values inside the details JSON field.

Run::

  $ seed-services-cli identity-details-update --help

to learn about the identity details update instructions.

Then to upload content create a JSON file ::

  $ seed-services-cli identity-details-update --json-file filename.json

Find demo_identities_details_update.json in the repo route for format example.

Messages Listing and Upload
---------------------------

Run::

  $ seed-services-cli sbm-messagesets --help

to learn about the messagesets available for uploading to.

Run::

  $ seed-services-cli sbm-messages-import --help

to learn about the message upload instructions.

Then to upload content create a CSV or JSON file ::

  $ seed-services-cli sbm-messages-import --csv filename.csv

Note: To upload binary content the file name should in the binary_content field
and this will be uploaded for you.

To retrieve messages run::

  $ seed-services-cli sbm-messages --help

Filters are available for message, messageset, lang and sequence_number.


Message Deletion
----------------

Run::

  $ seed-services-cli sbm-messages-delete --help

to learn about deleting messages. Filters are available for message,
messageset, lang and sequence_number.

Example that would purge all messages and binary files for messageset 1::

  $ seed-services-cli sbm-messages-delete --messageset 1


Registration Upload to Hub
---------------------------

Run::

  $ seed-services-cli hub-registrations-import --help

to learn about the registration upload instructions.

Then to upload content create a CSV or JSON file ::

  $ seed-services-cli hub-registrations-import --csv filename.csv

Find demo_import_registration.csv in the repo route for format example.


Adding Users to Auth with Team access
-------------------------------------

Run::

  $ seed-services-cli auth-user-add --help

to learn about adding users. Then add to a team.

Run::

  $ seed-services-cli auth-user-add-team --help


Checking Service status
-----------------------

Run::

  $ seed-services-cli ci-status

to get full service status uptime information.


Generate User Tokens
--------------------
Run::

  $ seed-services-cli ci-user-token-generate --help

to understand how to ensure Users have correct CI tokens for services.


Developing
----------------

Run::

  $ pip install --editable .

Testing::

  $ pip install -r requirements-dev.txt
  $ py.test seed_services_cli



Reporting issues
----------------

Issues can be filed in the GitHub issue tracker. Please don't use the issue
tracker for general support queries.

Release Notes
-------------
0.0.6 - 17-August-2016 - Added auth and ci related commands

0.0.5 - 14-July-2016 - Bugfix `identity-import` for malformed addresses

0.0.4 - 29-June-2016 - Added `hub-registrations-import`

0.0.3 - 29-June-2016 - Added `identity-get` and `identity-import`.

0.0.2 - 28-June-2016 - Added `sbm-messages-delete`. Renamed short param from `m` to `ms` for
messageset for `sbm-messages` command for consistency.

0.0.1 - Initial release
