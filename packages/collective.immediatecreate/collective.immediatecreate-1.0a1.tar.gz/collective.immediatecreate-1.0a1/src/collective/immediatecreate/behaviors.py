# -*- coding: utf-8 -*-
from zope.interface import Attribute
from zope.interface import Interface


class ICollectiveImmediateCreate(Interface):
    """Interface to enable immediate create status tracking.

    Also FTI needs the add information to make this work!
    """

    immediate_creation_status = Attribute(u"Was this item initially saved?")
