======================
Avi Networks Okta SDK
======================

Introduction
============
Provides a client abstraction to programmatically perform CRUD operations on resources in the
avinetworks Okta org.

Supported objects
-----------------
* Applications
* Users
* User groups
* Trusted origins
* API tokens

Design Overview
===============
The design philosphy is for client operations to achieve a desired state. Therefore if a resource
aleady exists, calling create on that same resource will simply return the existing resource.
Likewise a delete operations will succeed if the resource already does not exist. Calling get on
a non-existant resource will throw an exception.

Return Values
-------------
Most client methods will return a JSON representation of a resource, but a few such as delete
operations will return the status code of the API request.

Usage Examples
==============

Initialize an API client
------------------------
The client will typically be initizialized with an API token, but if you need to programatically
create API tokens you'll need to initialize with a username and password.

.. code-block:: python

    client = AviOktaClient(token='<your API token>')

Applications
------------
Only SAML application creation is supported for now.

.. code-block:: python

    app = client.create_app("my-app", "https://my-app.example.com")
    app['_created'] # True
    app = client.create_app("my-app")
    app['_created'] # False
    app = client.get_app(label="my-app")
    apps = client.list_apps()
    client.delete_app(app['id'])

Users
-----
User creation will also send a user activation email to the specified email address.
Application-user resources support up to ten tenant/role mappings with names *Tenant<n>*
and *Role<n>* where *<n>* is a number from 1 to 10.

.. code-block:: python

    user = client.create_user("FirstName", "LastName", "example@avinetworks.com")
    user = client.get_user(login="example@avinetorks.com")
    users = client.list_users()
    attrs = {'Tenant1': 'my-tenant', 'Role1': 'Tenant-Admin'}
    app_user = client.assign_user_to_app(app['id'], user['id'], attributes=attrs)
    client.delete_user(user['id'])

User Groups
-----------
.. code-block:: python

    group = client.create_group('my-group')
    group = client.get_group(name='my-group')
    groups = client.list_groups()
    client.assign_user_to_group(user['id'], group['id'])
    client.delete_group(group['id'])

Trusted Origins
---------------
.. code-block:: python

    trusted_origin = client.create_trusted_origin('My App', 'https://my-app.example.com', cors=False, redirect=True)

API Tokens
----------
Created tokens will be associated with the user who's credentials were used to initialize the client

.. code-block:: python

    token = client.create_token('my-token')
