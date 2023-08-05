# -*- coding: utf-8 -*-
from .behaviors import ICollectiveImmediateCreate
from plone.indexer.decorator import indexer


@indexer(ICollectiveImmediateCreate)
def index_in_immediate_creation(obj):
    if obj.collective_immediatecreate == "initial":
        return True
    raise AttributeError
