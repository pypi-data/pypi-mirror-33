# -*- coding: utf-8 -*-
from collective.preventactions.interfaces import ICollectivePreventActionsLayer
from collective.preventactions.interfaces import IPreventDelete
from collective.preventactions.interfaces import IPreventMoveOrRename
from collective.preventactions.testing import COLLECTIVE_PREVENTACTIONS_INTEGRATION  # noqa
from plone import api
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.browserlayer.utils import registered_layers
from zope.event import notify
from zope.interface import alsoProvides
from zope.traversing.interfaces import BeforeTraverseEvent

import unittest


class TestInstall(unittest.TestCase):
    layer = COLLECTIVE_PREVENTACTIONS_INTEGRATION

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        notify(BeforeTraverseEvent(self.portal, self.request))
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.document = api.content.create(container=self.portal,
                                           type='Document', id='document')
        self.document2 = api.content.create(container=self.portal,
                                            type='Document', id='document2')

    def test_product_is_installed(self):
        """ Validate that our products GS profile has been run and the product
            installed
        """
        qi_tool = api.portal.get_tool('portal_quickinstaller')
        pid = 'collective.preventactions'
        installed = [p['id'] for p in qi_tool.listInstalledProducts()]
        self.assertTrue(pid in installed,
                        'package appears not to have been installed')

    def test_layer_installed(self):
        self.assertTrue(ICollectivePreventActionsLayer in registered_layers())

    def test_uninstall_product(self):
        alsoProvides(self.document, IPreventDelete)
        alsoProvides(self.document2, IPreventDelete)
        alsoProvides(self.document2, IPreventMoveOrRename)
        self.document.reindexObject()
        self.document2.reindexObject()
        catalog = api.portal.get_tool('portal_catalog')
        query = {}
        query['object_provides'] = IPreventDelete.__identifier__
        brains = catalog(query)
        self.assertEqual(len(brains), 2)

        query['object_provides'] = IPreventMoveOrRename.__identifier__
        brains = catalog(query)
        self.assertEqual(len(brains), 1)

        applyProfile(self.portal, 'collective.preventactions:uninstall')
        self.assertFalse(ICollectivePreventActionsLayer in registered_layers())

        query['object_provides'] = IPreventDelete.__identifier__
        brains = catalog(query)
        self.assertEqual(len(brains), 0)

        query['object_provides'] = IPreventMoveOrRename.__identifier__
        brains = catalog(query)
        self.assertEqual(len(brains), 0)
