# -*- coding: utf-8 -*-
from collective.preventactions.interfaces import IPreventDelete
from collective.preventactions.interfaces import IPreventMoveOrRename
from plone import api
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer
from zope.interface import noLongerProvides


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller"""
        return [
            'collective.preventactions:uninstall',
        ]


def uninstall(context):
    # get all objects provided by IPreventDelete or IPreventMoveOrRename
    # for unprovided interfaces
    catalog = api.portal.get_tool('portal_catalog')
    query = {}
    for iface in [IPreventDelete, IPreventMoveOrRename]:
        query['object_provides'] = iface.__identifier__
        brains = catalog(query)
        for brain in brains:
            obj = brain.getObject()
            noLongerProvides(obj, iface)
            obj.reindexObject()
