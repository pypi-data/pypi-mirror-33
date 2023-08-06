# -*- coding: utf-8 -*-
from collective.preventactions.interfaces import IPreventDelete
from collective.preventactions.interfaces import IPreventMoveOrRename
from collective.preventactions.testing import COLLECTIVE_PREVENTACTIONS_INTEGRATION  # noqa
from OFS.ObjectManager import BeforeDeleteException
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME

from zope.interface import alsoProvides
from zope.interface import noLongerProvides

import unittest


class TestActions(unittest.TestCase):
    layer = COLLECTIVE_PREVENTACTIONS_INTEGRATION

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.document = api.content.create(container=self.portal,
                                           type='Document', id='document')

    def test_delete_document(self):
        login(self.portal, TEST_USER_NAME)
        alsoProvides(self.document, IPreventDelete)
        self.assertTrue('document' in self.portal.contentIds())
        self.assertRaises(BeforeDeleteException,
                          api.content.delete, self.document)
        self.assertTrue('document' in self.portal.contentIds())

    def test_move_document(self):
        login(self.portal, TEST_USER_NAME)
        self.folder = api.content.create(
            container=self.portal, type='Folder', id='folder')
        alsoProvides(self.document, IPreventMoveOrRename)
        self.assertEqual(self.document.absolute_url(),
                         'http://nohost/plone/document')

        self.assertRaises(Exception,
                          api.content.move, self.document, self.folder)

        self.assertRaises(Exception,
                          api.content.rename, self.document, 'changed-doc')
        # api.content.move(source=self.document, target=self.folder)
        self.assertEqual(self.document.absolute_url(),
                         'http://nohost/plone/document')

        noLongerProvides(self.document, IPreventMoveOrRename)
        api.content.rename(obj=self.document, new_id='old-doc')
        self.assertEqual(self.document.id, 'old-doc')

        alsoProvides(self.document, IPreventMoveOrRename)
        alsoProvides(self.document, IPreventDelete)
        self.assertRaises(Exception,
                          api.content.move, self.document, self.folder)

        self.assertRaises(Exception,
                          api.content.rename, self.document, 'changed-doc')
        # api.content.move(source=self.document, target=self.folder)
        self.assertEqual(self.document.absolute_url(),
                         'http://nohost/plone/old-doc')

        noLongerProvides(self.document, IPreventMoveOrRename)
