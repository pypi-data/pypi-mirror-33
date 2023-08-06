.. -*- coding: utf-8 -*-
.. :Project:   metapensiero.sqlalchemy.proxy -- Pyramid specific stuff
.. :Created:   ven 30 dic 2016 18:48:01 CET
.. :Author:    Lele Gaifax <lele@metapensiero.it>
.. :License:   GNU General Public License version 3 or later
.. :Copyright: © 2016, 2017, 2018 Lele Gaifax
..

==============
 With Pyramid
==============

Since version 1.7 there are some Pyramid__ specific subclasses that help using the proxies
within a Pyramid view as well as a `expose` decorator that simplify their implementation.

__ https://trypyramid.com/


.. module:: metapensiero.sqlalchemy.proxy.pyramid

.. class:: expose(proxable, metadata=None, adaptor=None, POST=True, **kw)

   Decorator to simplify exposition of a SQLAlchemy Query.

   :param proxable: either a SQLAlchemy Query or a mapped class
   :param metadata: a dictionary with additional info about the fields
   :param adaptor: if given, it's a function that will be called to adapt incoming data before
      actually writing it to the database.
   :type POST: either a boolean flag or a function, ``True`` by default
   :keyword POST: whether to handle POST request: if ``True`` a standard function will be used,
      otherwise it must be a function accepting two positional arguments, respectively the
      SQLAlchemy session and the Pyramid request object, and a set of keyword arguments
      corresponding to the changed field

   This is an helper class that aids the exposition of either a SQLAlchemy Query or directly a
   mapped class as a Pyramid view.

   User of this class **must** inject a concrete implementation of the :meth:`create_session`
   and :meth:`save_changes` static methods. This is usually done once at application startup,
   for example:

   .. code-block:: python

       from ..models import DBSession
       from ..models.utils import save_changes

       # Configure the `expose` decorator
       expose.create_session = staticmethod(lambda req: DBSession())
       expose.save_changes = staticmethod(save_changes)

   Another *class* method that may eventually be replaced is :meth:`extract_parameters`: the
   default implementation simply returns a copy of the `request.params` dictionary, but
   sometimes it is desiderable to pass additional parameters, for example when using
   `bindparams`:

   .. code-block:: python

       def _extract_parameters(request):
           "Build a dictionary of arguments for the proxy from the current request"

           parameters = dict(request.params)
           # The following feeds eventual `bindparams`
           parameters['params'] = dict(request.session)
           return parameters

       expose.extract_parameters = staticmethod(_extract_parameters)

   The typical usage is:

   .. code-block:: python

       @view_config(route_name='users', renderer='json')
       @expose(User, metadata=dict(
           password=dict(hidden=True, password=True, width=40),
           is_anonymous=False,
           ))
       def users(request, results):
           return results

   The first argument may be either a mapped class or a query.

   The decorated function is finally called with the current request and the result of the
   operation, and it can eventually adjust the `results` dictionary.

   The decorated function may be a generator instead, which has the opportunity of freely
   manipulate either the arguments received from the request, or the final result, or both as
   follows:

   .. code-block:: python

       @expose(User, metadata=dict(
           password=dict(hidden=True, password=True, width=40),
           is_anonymous=False,
           ))
       def complex():
           # Receive request and params
           request, params = (yield)
           log.debug('REQUEST: %r', request)

           # Adjust parameters
           params['new'] = True

           if 'something' in params:
               # Inject other conditions
               something = params.pop('something')
               conditions = (User.c.foo == something,)
               result = yield params, conditions
           else:
               # Go on, and receive the final result
               result = yield params

           # Fix it up
           result['COMPLEX'] = 'MAYBE'

           yield result

   As you can see, in this case the decorated function shall not declare any formal argument,
   because it receives its "feed" as the result of the ``yield`` expressions.

   .. staticmethod:: create_session(request)

      Create a new SQLAlchemy session, given the current request.

   .. staticmethod:: extract_parameters(request)

      Create a dictionary of parameters from the current request.

   .. staticmethod:: save_changes(sa_session, modified, deleted)

      Save insertions, changes and deletions to the database.

      :param sa_session: the SQLAlchemy session
      :param modified: a sequence of record changes, each represented by a tuple of two items,
          the PK name and a dictionary with the modified fields; if the value of the PK field
          is null or 0 then the record is considered new and will be inserted instead of
          updated
      :param deleted: a sequence of deletions, each represented by a tuple of two items, the PK
          name and the ID of the record to be removed
      :rtype: a tuple of three lists, respectively inserted, modified and deleted record IDs,
          grouped in a dictionary keyed on PK name.


Basic setup
===========

First of all, there are some setup steps to follow:

1. Include the package in the configuration file::

    [app:main]
    use = egg:ph.data

    ...

    pyramid.includes =
        metapensiero.sqlalchemy.proxy.pyramid
        pyramid_tm

   This is not strictly needed, but it will override the standard ``json`` renderer with one
   that uses ``nssjson``, to handle the datetime type.

2. Configure the ``expose`` decorator, for example adding something like the following snippet
   to the ``.../views.py`` source:

   .. code-block:: python

    from metapensiero.sqlalchemy.proxy.pyramid import expose
    from .models import DBSession

    # Configure the `expose` decorator
    expose.create_session = staticmethod(lambda req: DBSession())

Then you can add views to expose either an entity or a plain select:

.. code-block:: python

    @view_config(route_name='users', renderer='json')
    @expose(User, metadata=dict(
        password=dict(hidden=True, password=True, width=40),
        active=dict(default=True),
        is_anonymous=False,
        ))
    def users(request, results):
        return results

    sessions_t = Session.__table__

    @view_config(route_name='sessions', renderer='json')
    @expose(select([sessions_t], sessions_t.c.iduser == bindparam('user_id')))
    def sessions(request, results):
        return results

The decorated function may be a generator instead, which has the opportunity of freely
manipulate either the arguments received from the request, or the final result, or both as
follows:

.. code-block:: python

    @view_config(route_name='users', renderer='json')
    @expose(User, metadata=dict(
        password=dict(hidden=True, password=True, width=40),
        active=dict(default=True),
        is_anonymous=False,
        ))
    def complex():
        # Receive request and arguments
        request, args = (yield)

        # Adjust parameters
        args['new'] = True

        # Note that bindparams by default are extracted from the “params”
        # keyword argument
        bindparams = args.setdefault('params', {})
        bindparams['user_id'] = 2

        if 'something' in params:
            # Inject other conditions
            something = args.pop('something')
            conditions = (User.c.foo == something,)
            result = yield args, conditions
        else:
            # Go on, and receive the final result
            result = yield args

        # Fix it up
        result['COMPLEX'] = 'MAYBE'

        yield result


Request examples
----------------

Assuming the ``users`` view is added as ``/views/users``, it could be called in the following
ways:

``GET /views/users``
  would return a JSON response containing **all** users, like::

    {
      "count": 1234,
      "message": "Ok",
      "success": true,
      "root": [
        {
          "first_name": "Lele",
          "last_name": "Gaifax",
          ...
        },
        {
          "first_name": "Mario",
          "last_name": "Rossi",
          ...
        },
        ...
      ]
    }

``GET /views/users?limit=1&start=2``
  would return a JSON response containing just **one** user, the second::

    {
      "count": 1234,
      "message": "Ok",
      "success": true,
      "root": [
        {
          "first_name": "Mario",
          "last_name": "Rossi",
          ...
        }
      ]
    }

``GET /views/users?filter_by_first_name=Lele``
  would return a JSON response containing the records satisfying the given condition::

    {
      "count": 1,
      "message": "Ok",
      "success": true,
      "root": [
        {
          "first_name": "Lele",
          "last_name": "Gaifax",
          ...
        }
      ]
    }

``GET /views/users?filter_col=first_name&filter_value=Lele``
  same as above

``GET /views/users?limit=1&only_cols=first_name,role_name``
  would return a JSON response containing only the requested fields of a single record::

    {
      "count": 1234,
      "message": "Ok",
      "success": true,
      "root": [
        {
          "first_name": "Lele",
          "role_name": "administrator"
        }
      ]
    }

``GET /views/users?metadata=metadata&limit=0``
  would return a JSON response containing a description of the schema::

    {
      "metadata": {
        "success_slot": "success",
        "primary_key": "iduser",
        "fields": [
          {
            "width": 60,
            "hint": "The unique ID of the user.",
            "align": "right",
            "nullable": false,
            "readonly": true,
            "type": "int",
            "hidden": true,
            "label": "User ID",
            "name": "iduser"
          },
          {
            "type": "boolean",
            "label": "Active",
            "hint": "Whether the user is currently active.",
            "name": "active",
            "default": true
            ...
          }
          ...
        ],
        "root_slot": "root",
        "count_slot": "count"
      },
      "message": "Ok",
      "success": true
    }

Browse SoL__ sources for real usage examples.

__ https://bitbucket.org/lele/sol/src/master/src/sol/views/data.py


Obtaining original instances
============================

By default the decorator configures the proxy to return plain Python dictionaries, but sometime
you may need to manipulate the resultset in way that it is easier done working with the actual
instances.

In such cases you can explicitly pass ``asdict=False`` and then convert the list of instances
to a JSON-serializable list of dictionaries by yourself, for example with something like the
following, where the ``Image`` class is using `sqlalchemy-media`__ to store image details in
the ``image`` field, backed by a ``JSONB`` column, of the class:

.. code-block:: python

    @view_config(route_name='images', renderer='json')
    @expose(
        Image,
        asdict=False, fields=('id', 'position', 'width', 'height', 'original_filename'),
        metadata=dict(
            height=dict(label=_('Height'),
                        hint=_('The height of the image.')),
            original_filename=dict(label=_('Name'),
                                   hint=_('Original name of the image.')),
            width=dict(label=_('Width'),
                       hint=_('The width of the image.'))))
    def listing(request, results):
        root = results.get('root')
        if root:
            results['root'] = newroot = []
            for image in root:
                img = image.image
                d = {'id': image.id, 'position': image.position,
                     'width': img['width'], 'height': img['height'],
                     'original_filename': img['original_filename']}
                thumbnail = img.get_thumbnail(width=200, auto_generate=True)
                d['image_url'] = thumbnail.locate()
                newroot.append(d)
        return results

__ http://sqlalchemy-media.dobisel.com/index.html
