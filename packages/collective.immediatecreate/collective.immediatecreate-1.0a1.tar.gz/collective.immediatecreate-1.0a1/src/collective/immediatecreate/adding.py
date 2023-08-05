# -*- coding: utf-8 -*-
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.protect.utils import addTokenToUrl
from Products.Five.browser import BrowserView
from zExceptions import Unauthorized
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.location.interfaces import LocationError
from zope.traversing.interfaces import ITraversable


class ImmediateAddView(BrowserView):
    def __init__(self, context, request, fti):
        super(ImmediateAddView, self).__init__(context, request)
        self.fti = fti

    def __call__(self):
        # construct content
        if not self.fti.isConstructionAllowed(self.context):
            raise Unauthorized()
        newcontent = api.content.create(
            container=self.context,
            type=self.fti.getId(),
            id="new-{0:s}".format(self.fti.getId()),
            safe_id=True,
            collective_immediatecreate="initial",
        )
        newcontent.indexObject()
        alsoProvides(self.request, IDisableCSRFProtection)
        url = newcontent.absolute_url() + "/editimmediate"
        url = addTokenToUrl(url)
        self.request.response.redirect(url)


@implementer(ITraversable)
class ImmediateAddViewTraverser(object):

    """Immediate add view traverser.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, ignored):
        ttool = api.portal.get_tool("portal_types")
        fti = ttool.getTypeInfo(name)
        if fti is None:
            raise LocationError(self.context, name)
        return ImmediateAddView(self.context, self.request, fti)
