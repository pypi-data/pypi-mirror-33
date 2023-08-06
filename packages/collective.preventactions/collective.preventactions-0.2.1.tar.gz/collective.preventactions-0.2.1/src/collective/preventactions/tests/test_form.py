# -*- coding: utf-8 -*-
from collective.preventactions.browser.preventactions import PreventActionsForm
from collective.preventactions.interfaces import IPreventDelete
from collective.preventactions.interfaces import IPreventMoveOrRename
from collective.preventactions.testing import COLLECTIVE_PREVENTACTIONS_INTEGRATION  # noqa
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from zope.interface import alsoProvides
from zope.interface import noLongerProvides

import unittest


class TestForm(unittest.TestCase):
    layer = COLLECTIVE_PREVENTACTIONS_INTEGRATION

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.document = api.content.create(container=self.portal,
                                           type='Document', id='document')

    def test_form_checked_options(self):
        login(self.portal, TEST_USER_NAME)
        alsoProvides(self.document, IPreventDelete)
        form = PreventActionsForm(self.document, self.request)
        form.updateWidgets()

        widget = form.widgets.get('delete')
        delete_widget_value = widget.items[0]
        self.assertTrue(delete_widget_value['checked'])
        widget = form.widgets.get('move_or_rename')
        move_or_rename_widget_value = widget.items[0]
        self.assertFalse(move_or_rename_widget_value['checked'])

        noLongerProvides(self.document, IPreventDelete)
        form.updateWidgets()

        widget = form.widgets.get('delete')
        delete_widget_value = widget.items[0]
        self.assertFalse(delete_widget_value['checked'])
        widget = form.widgets.get('move_or_rename')
        move_or_rename_widget_value = widget.items[0]
        self.assertFalse(move_or_rename_widget_value['checked'])

        alsoProvides(self.document, IPreventMoveOrRename)
        form.updateWidgets()

        widget = form.widgets.get('delete')
        delete_widget_value = widget.items[0]
        self.assertFalse(delete_widget_value['checked'])
        widget = form.widgets.get('move_or_rename')
        move_or_rename_widget_value = widget.items[0]
        self.assertTrue(move_or_rename_widget_value['checked'])
