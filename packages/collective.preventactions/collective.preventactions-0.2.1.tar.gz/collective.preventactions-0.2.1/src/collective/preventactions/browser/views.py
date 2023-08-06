# -*- coding: utf-8 -*-
from collective.preventactions.interfaces import IPreventDelete
from collective.preventactions.interfaces import IPreventMoveOrRename
from Products.Five.browser import BrowserView


class IsDeletable(BrowserView):
    """ Return True if we can delete object
    """

    def __call__(self):
        return not IPreventDelete.providedBy(self.context)


class IsMoveable(BrowserView):
    """  Return True if we can move or rename object
    """

    def __call__(self):
        return not IPreventMoveOrRename.providedBy(self.context)
