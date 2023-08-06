.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.
   
.. image:: https://travis-ci.org/collective/collective.preventactions.svg?branch=master
   :target: https://travis-ci.org/collective/collective.preventactions

.. image:: https://coveralls.io/repos/collective/collective.preventactions/badge.svg?branch=master
   :target: https://coveralls.io/github/collective/collective.preventactions?branch=master

=========================
collective.preventactions
=========================

This package allows administrateur to marker object which can't be deleted or renamed/moved.

.. image:: https://raw.githubusercontent.com/imio/collective.preventactions/master/docs/screenshot.png
    :alt: The map on a collection.
    :width: 388
    :height: 276
    :align: center
    
* `Source code @ GitHub <https://github.com/collective/collective.preventactions>`_
* `Releases @ PyPI <http://pypi.python.org/pypi/collective.preventactions>`_

How it works
------------

This package use marker interfaces and subscribe to `IObjectWillBeRemovedEvent` and `IObjectWillBeMovedEvent` events.
If a marker interface is find on modified object, a exception will be raised.

You can also set some contents not deleteable (for example) like this in your setuphandler : ::

   from collective.preventactions.interfaces import IPreventDelete
   from plone import api
   from zope.interface import alsoProvides
   
   
   def post_install(context):
       obj = api.content.get('/Plone/content-not-deleteable')
       alsoProvides(obj, IPreventDelete)

Installation
------------

To install `collective.preventactions` you simply add ``collective.preventactions``
to the list of eggs in your buildout, run buildout and restart Plone.

Then, install `collective.preventactions` using the Add-ons control panel.



License
-------

The project is licensed under the GPLv2.
