# -*- coding: utf-8 -*-
from collective.immediatecreate import _
from plone import api
from Products.Five.browser import BrowserView

import datetime


TWO_HOURS = datetime.timedelta(hours=2)


class CleanupImmediateLeftovers(BrowserView):
    def __call__(self):
        two_hour_ago = datetime.datetime.now() - TWO_HOURS
        brains = api.content.find(
            in_immediate_creation=True,
            created={"query": two_hour_ago, "range": "max"},
        )
        objs = [b.getObject() for b in brains]
        count = len(objs)
        if count == 0:
            api.portal.show_message(
                _(u"cleanup_delete_nothing", (u"Nothing to delete")),
                request=self.request,
            )
            self.request.response.redirect(self.context.absolute_url())
        api.content.delete(objects=objs)
        api.portal.show_message(
            _(
                u"cleanup_delete",
                (
                    u"${count} items left in creation state for more than two "
                    u"hours deleted."
                ),
                mapping={"count": count},
            ),
            request=self.request,
        )
        self.request.response.redirect(self.context.absolute_url())
