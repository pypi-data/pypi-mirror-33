# -*- coding: utf-8 -*-
from zope.interface import Interface


class ICollectivePreventActionsLayer(Interface):
    """Marker interface that defines a Zope 3 browser layer."""


class IPreventDelete(Interface):
    """Marker interface for prevent delete object"""


class IPreventMoveOrRename(Interface):
    """Marker interface for prevent move / rename object"""
