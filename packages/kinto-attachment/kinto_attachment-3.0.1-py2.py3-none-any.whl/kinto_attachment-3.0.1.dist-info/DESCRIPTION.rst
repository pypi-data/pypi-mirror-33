================
Kinto Attachment
================

.. image:: https://img.shields.io/travis/Kinto/kinto-attachment/master.svg
        :target: https://travis-ci.org/Kinto/kinto-attachment

.. image:: https://img.shields.io/pypi/v/kinto-attachment.svg
        :target: https://pypi.python.org/pypi/kinto-attachment

.. image:: https://coveralls.io/repos/Kinto/kinto-attachment/badge.svg?branch=master
        :target: https://coveralls.io/r/Kinto/kinto-attachment

Attach files to `Kinto records <http://kinto.readthedocs.io>`_.


Install
=======

::

    pip install kinto-attachment


Setup
=====

In the Kinto project settings

.. code-block:: ini

    kinto.includes = kinto_attachment
    kinto.attachment.base_url = http://cdn.service.org/files/
    kinto.attachment.folder = {bucket_id}/{collection_id}
    kinto.attachment.keep_old_files = true


The ``gzipped`` option
----------------------

If you want uploaded files to get gzipped when stored:

.. code-block:: ini

    kinto.attachment.gzipped = true


The ``use_content_encoding`` option
-----------------------------------

If you want uploaded files to be Gzipped and automatically unzipped on the client side
when downloading with S3 you can activate the content encoding setting:

.. code-block:: ini

    kinto.attachment.use_content_encoding = true

In case you want to activate ``gzipped`` for some buckets or
collections and activate ``use_content_encoding`` for some other, you
can use the resource configuration key:

.. code-block:: ini

    # For a whole bucket (/buckets/fennec-staging)
    kinto.attachment.resources.fennec-staging.use_content_encoding = false
    kinto.attachment.resources.fennec-staging.gzipped = true

    # Or for a specific collection in it (/buckets/fingerprinting-defenses-staging/fonts)
    kinto.attachment.resources.fingerprinting-defenses-staging.fonts.use_content_encoding = true

Be careful, ``use_content_encoding`` automatically sets ``gzipped =
true`` with the S3 storage but the metadata will look like it wasn't
compressed.

In case you want to use the ``gzipped`` option you need to also make
sure that ``use_content_encoding`` is set to `False`.

You can say that you want to use content encoding everywhere but for
the ``fennec-staging`` bucket:

.. code-block:: ini

    # Global setting
    kinto.attachment.use_content_encoding = true

    # For a whole bucket (/buckets/fennec-staging)
    kinto.attachment.resources.fennec-staging.use_content_encoding = false
    kinto.attachment.resources.fennec-staging.gzipped = true

Or that you want to use ``gzipped`` everywhere but for the
``fingerprinting-defenses-staging`` bucket:

.. code-block:: ini

    # Global default setting
    kinto.attachment.gzipped = true

    # For a whole bucket (/buckets/fennec-staging)
    kinto.attachment.resources.fingerprinting-defenses-staging.use_content_encoding = true


Local File storage
------------------

Store files locally:

.. code-block:: ini

    kinto.attachment.base_path = /tmp

S3 File Storage
---------------

Store on Amazon S3:

.. code-block:: ini

    kinto.attachment.aws.access_key = <AWS access key>
    kinto.attachment.aws.secret_key = <AWS secret key>
    kinto.attachment.aws.bucket_name = <bucket name>
    kinto.attachment.aws.acl = <AWS ACL permissions|public-read>


.. note::

    ``access_key`` and ``secret_key`` may be omitted when using AWS Identity
    and Access Management (IAM).

See `Pyramid Storage <https://pythonhosted.org/pyramid_storage/>`_.


Default bucket
--------------

In order to upload files on the ``default`` bucket, the built-in default bucket
plugin should be enabled before the ``kinto_attachment`` plugin.

In the configuration, this means adding it explicitly to includes:

.. code-block:: ini

    kinto.includes = kinto.plugins.default_bucket
                     kinto_attachment

Production
----------

* Make sure the ``base_url`` can be reached (and points to ``base_path`` if
  files are stored locally)
* Adjust the max size for uploaded files (e.g. ``client_max_body_size 10m;`` for NGinx)

For example, with NGinx

::

    server {
        listen 80;

        location /v1 {
            ...
        }

        location /files {
            root /var/www/kinto;
        }
    }


API
===

**POST /{record-url}/attachment**

It will create the underlying record if it does not exist.

Required

- ``attachment``: a single multipart-encoded file

Optional

- ``data``: attributes to set on record (serialized JSON)
- ``permissions``: permissions to set on record (serialized JSON)


**DELETE /{record-url}/attachment**

Deletes the attachement from the record.

QueryString options
-------------------

By default, the server will randomize the name of the attached files. If you
don't want this behavior and prefer to keep the original file name, you can
pass ``?randomize=false`` in the QueryString.

By default, the server won't gzip files unless you specifically used the
``kinto.attachment.gzipped`` option if you want to **force** gzip to all
collections.

You can overwite that option by passing a ``?gzipped=true`` in the QueryString
to specifically gzip some files.

By default, the server will serve the gzip file, if you want the HTTP
client to automatically decompress the file while loading it from S3 you can
specify it when uploading the file by passing a ``?use_content_encoding=true``


Attributes
----------

When a file is attached, the related record is given an ``attachment`` attribute
with the following fields:

- ``filename``: the original filename
- ``hash``: a SHA-256 digest
- ``location``: the URL of the attachment
- ``mimetype``: the `media type <https://en.wikipedia.org/wiki/Media_type>`_ of
  the file
- ``size``: size in bytes

.. code-block:: json

    {
        "data": {
            "attachment": {
                "filename": "IMG_20150219_174559.jpg",
                "hash": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
                "location": "http://cdn.service.org/files/ffa9c7b9-7561-406b-b7f9-e00ac94644ff.jpg",
                "mimetype": "image/jpeg",
                "size": 1481798
            },
            "id": "c2ce1975-0e52-4b2f-a5db-80166aeca688",
            "last_modified": 1447834938251,
            "theme": "orange",
            "type": "wallpaper"
        },
        "permissions": {
            "write": ["basicauth:6de355038fd943a2dc91405063b91018bb5dd97a08d1beb95713d23c2909748f"]
        }
    }


If the file is gzipped by the server, an ``original`` key is added in the ``attachment``
key, containing the file info **before** it's gzipped. The ``attachment`` keys are
in that case referring to the gzipped file:


.. code-block:: json

    {
        "data": {
            "attachment": {
                "filename": "IMG_20150219_174559.jpg.gz",
                "hash": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
                "location": "http://cdn.service.org/files/ffa9c7b9-7561-406b-b7f9-e00ac94644ff.jpg.gz",
                "mimetype": "application/x-gzip",
                "size": 14818,
                "original": {
                    "filename": "IMG_20150219_174559.jpg",
                    "hash": "hPME6i9avCf/LFaznYr+sHtwQEX7mXYHSu+vgtygpM8=",
                    "mimetype": "image/jpeg",
                    "size": 1481798
                }
            },
            "id": "c2ce1975-0e52-4b2f-a5db-80166aeca688",
            "last_modified": 1447834938251,
            "theme": "orange",
            "type": "wallpaper"
        },
        "permissions": {
            "write": ["basicauth:6de355038fd943a2dc91405063b91018bb5dd97a08d1beb95713d23c2909748f"]
        }
    }




Usage
=====

Using HTTPie
------------

.. code-block:: bash

    http --auth alice:passwd --form POST http://localhost:8888/v1/buckets/website/collections/assets/records/c2ce1975-0e52-4b2f-a5db-80166aeca689/attachment data='{"type": "wallpaper", "theme": "orange"}' "attachment@~/Pictures/background.jpg"

.. code-block:: http

    HTTP/1.1 201 Created
    Access-Control-Expose-Headers: Retry-After, Content-Length, Alert, Backoff
    Content-Length: 209
    Content-Type: application/json; charset=UTF-8
    Date: Wed, 18 Nov 2015 08:22:18 GMT
    Etag: "1447834938251"
    Last-Modified: Wed, 18 Nov 2015 08:22:18 GMT
    Location: http://localhost:8888/v1/buckets/website/collections/font/assets/c2ce1975-0e52-4b2f-a5db-80166aeca689
    Server: waitress

    {
        "filename": "IMG_20150219_174559.jpg",
        "hash": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        "location": "http://cdn.service.org/files/ffa9c7b9-7561-406b-b7f9-e00ac94644ff.jpg",
        "mimetype": "image/jpeg",
        "size": 1481798
    }


Using Python requests
---------------------

.. code-block:: python

    auth = ("alice", "passwd")
    attributes = {"type": "wallpaper", "theme": "orange"}
    perms = {"read": ["system.Everyone"]}

    files = [("attachment", ("background.jpg", open("Pictures/background.jpg", "rb"), "image/jpeg"))]

    payload = {"data": json.dumps(attributes), "permissions": json.dumps(perms)}
    response = requests.post(SERVER_URL + endpoint, data=payload, files=files, auth=auth)

    response.raise_for_status()


Using JavaScript
----------------

.. code-block:: javascript

    var headers = {Authorization: "Basic " + btoa("alice:passwd")};
    var attributes = {"type": "wallpaper", "theme": "orange"};
    var perms = {"read": ["system.Everyone"]};

    // File object from input field
    var file = form.elements.attachment.files[0];

    // Build form data
    var payload = new FormData();
    // Multipart attachment
    payload.append('attachment', file, "background.jpg");
    // Record attributes and permissions JSON encoded
    payload.append('data', JSON.stringify(attributes));
    payload.append('permissions', JSON.stringify(perms));

    // Post form using GlobalFetch API
    var url = `${server}/buckets/${bucket}/collections/${collection}/records/${record}/attachment`;
    fetch(url, {method: "POST", body: payload, headers: headers})
      .then(function (result) {
        console.log(result);
      });


Scripts
=======

Two scripts are provided in this repository.

They rely on the ``kinto-client`` Python package, which can be installed in a
virtualenv:

::

    $ virtualenv env --python=python3
    $ source env/bin/activate
    $ pip install kinto-client

Or globally on your system (**not recommended**):

::

    $ sudo pip install kinto-client


Upload files
------------

``upload.py`` takes a list of files and posts them on the specified server,
bucket and collection::

    $ python3 scripts/upload.py --server=$SERVER --bucket=$BUCKET --collection=$COLLECTION --auth "token:mysecret" README.rst pictures/*

If the ``--gzip`` option is passed, the files are gzipped before upload.
Since the ``attachment`` attribute contains metadata of the compressed file
the original file metadata are stored in a ``original`` attribute.

See ``python3 scripts/upload.py --help`` for more details about options.

Download files
--------------

``download.py`` downloads the attachments from the specified server, bucket and
collection and store them on disk::

    $ python3 scripts/download.py --server=$SERVER --bucket=$BUCKET --collection=$COLLECTION --auth "token:mysecret"

If the record has an ``original`` attribute, the script decompresses the attachment
after downloading it.

Files are stored in the current folder by default.
See ``python3 scripts/download.py --help`` for more details about options.


Known limitations
=================

* No support for chunk upload (#10)
* Files are not removed when server is purged with ``POST /v1/__flush__``

Relative URL in records (workaround)
------------------------------------

Currently the full URL is returned in records. This is very convenient for API consumers
which can access the attached file just using the value in the ``location`` attribute.

However, the way it is implemented has a limitation: the full URL is stored in each record
directly. This is annoying because changing the ``base_url`` setting
won't actually change the ``location`` attributes on existing records.

As workaround, it is possible to set the ``kinto.attachment.base_url`` to an empty
value. The ``location`` attribute in records will now contain a *relative* URL.

Using another setting ``kinto.attachment.extra.base_url``, it is possible to advertise
the base URL that can be preprended by clients to obtain the full attachment URL.
If specified, it is going to be exposed in the capabilities of the root URL endpoint.


Run tests
=========

Run a fake Amazon S3 server in a separate terminal::

    make moto

Run the tests suite::

    make tests


Notes
=====

* `API design discussion <https://github.com/Kinto/kinto/issues/256>`_ about mixing up ``attachment`` and record fields.


Changelog
=========

3.0.1 (2018-07-05)
------------------

**Bug fix**

- Do not delete attachment when record is deleted if ``keep_old_files`` setting is true (#137)


3.0.0 (2018-04-10)
------------------

**Breaking changes**

- The collection specific ``use_content_encoding`` setting must now be separated with ``.`` instead of ``_``.
  (eg. use ``kinto.attachment.resources.bid.cid.use_content_encoding`` instead of ``kinto.attachment.resources.bid_cid.use_content_encoding``) (fixes #134)


2.1.0 (2017-12-06)
------------------

**New features**

- Add support for the ``Content-Encoding`` header with the S3Backend (#132)


2.0.1 (2017-04-06)
------------------

**Bug fixes**

- Set request parameters before instantiating a record resource. (#127)


2.0.0 (2017-03-03)
------------------

**Breaking changes**

- Remove Python 2.7 support and upgrade to Python 3.5. (#125)


1.1.2 (2017-02-01)
------------------

**Bug fixes**

- Fix invalid request when attaching a file on non UUID record id (fixes #122)


1.1.1 (2017-02-01)
------------------

**Bug fixes**

- Fixes compatibility with Kinto 5.3 (fixes #120)


1.1.0 (2016-12-16)
------------------

- Expose the gzipped settings value in the capability (#117)


1.0.1 (2016-11-04)
------------------

**Bug fixes**

- Make kinto-attachment compatible with both cornice 1.x and 2.x (#115)


1.0.0 (2016-09-07)
------------------

**Breaking change**

- Remove the ``base_url`` from the public settings because the
  accurate value is in the capability.

**Protocol**

- Add the plugin version in the capability.


0.8.0 (2016-07-18)
------------------

**New features**

- Prevent ``attachment`` attributes to be modified manually (fixes #83)

**Bug fixes**

- Fix crash when the file is not uploaded using ``attachment`` field name (fixes #57)
- Fix crash when the multipart content-type is invalid.
- Prevent crash when filename is not provided (fixes #81)
- Update the call to the Record resource to use named attributes. (#97)
- Show detailed error when data is not posted with multipart content-type.
- Fix crash when submitted data is not valid JSON (fixes #104)

**Internal changes**

- Remove hard-coded CORS setup (fixes #59)


0.7.0 (2016-06-10)
------------------

- Add the gzip option to automatically gzip files on upload (#85)
- Run functional test on latest kinto release as well as kinto master (#86)


0.6.0 (2016-05-19)
------------------

**Breaking changes**

- Update to ``kinto.core`` for compatibility with Kinto 3.0. This
  release is no longer compatible with Kinto < 3.0, please upgrade!

**New features**

- Add a ``kinto.attachment.extra.base_url`` settings to be exposed publicly. (#73)


0.5.1 (2016-04-14)
------------------

**Bug fixes**

- Fix MANIFEST.in rules


0.5.0 (2016-04-14)
------------------

**New features**

- Add ability to disable filename randomization using a ``?randomize=false`` querystring (#62)
- Add a ``--keep-filenames`` option in ``upload.py`` script to disable randomization (#63)

**Bug fixes**

- Fix a setting name for S3 bucket in README (#68)
- Do nothing in heartbeat if server is readonly (fixes #69)

**Internal changes**

- Big refactor of views (#61)


0.4.0 (2016-03-09)
------------------

**New features**

- Previous files can be kept if the setting ``kinto.keep_old_files`` is set
  to ``true``. This can be useful when clients try to download files from a
  collection of records that is not up-to-date.
- Add heartbeat entry for attachments backend (#41)

**Bug fixes**

- Now compatible with the default bucket (#42)
- Now compatible with Python 3 (#44)

**Internal changes**

- Upload/Download scripts now use ``kinto.py`` (#38)


0.3.0 (2016-02-05)
------------------

**New feature**

- Expose the API capability ``attachments`` in the root URL (#35)

**Internal changes**

- Upgrade tests for Kinto 1.11.0 (#36)


0.2.0 (2015-12-21)
------------------

**New feature**

- Setting to store files into folders by bucket or collection (fixes #22)

**Bug fixes**

- Remove existing file when attachment is replaced (fixes #28)

**Documentation**

- The demo is now fully online, since the Mozilla demo server has this plugin
  installed.
- Add some minimal information for production


0.1.0 (2015-12-02)
------------------

* Initial working proof-of-concept.


