# -*- coding: utf-8 -*-
from collective.preventactions.interfaces import IPreventDelete
from collective.preventactions.testing import COLLECTIVE_PREVENTACTIONS_INTEGRATION  # noqa
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from zope.interface import alsoProvides

import unittest


class TestViews(unittest.TestCase):
    layer = COLLECTIVE_PREVENTACTIONS_INTEGRATION

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.document = api.content.create(container=self.portal,
                                           type='Document', id='document')

    def test_is_deletable_view(self):
        login(self.portal, TEST_USER_NAME)
        alsoProvides(self.document, IPreventDelete)
        view = self.document.restrictedTraverse('is_deletable')()
        self.assertFalse(view)

    def test_is_moveable_view(self):
        view = self.document.restrictedTraverse('is_moveable')()
        self.assertTrue(view)
