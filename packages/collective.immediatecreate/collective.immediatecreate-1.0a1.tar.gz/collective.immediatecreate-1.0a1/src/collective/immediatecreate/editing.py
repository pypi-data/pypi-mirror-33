# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from collective.immediatecreate import _
from plone import api
from plone.dexterity.browser.base import DexterityExtensibleForm
from plone.dexterity.events import EditBegunEvent
from plone.dexterity.events import EditCancelledEvent
from plone.dexterity.events import EditFinishedEvent
from plone.dexterity.i18n import MessageFactory as _dx
from plone.dexterity.interfaces import IDexterityEditForm
from plone.dexterity.interfaces import IDexterityFTI
from plone.protect.utils import addTokenToUrl
from plone.registry.interfaces import IRegistry
from plone.z3cform import layout
from z3c.form import button
from z3c.form import form
from zExceptions import Redirect
from zope.component import getUtility
from zope.container.interfaces import INameChooser
from zope.event import notify
from zope.interface import classImplements


class ImmediateEditForm(DexterityExtensibleForm, form.EditForm):

    success_message = _(u"New content saved")

    @button.buttonAndHandler(_dx(u"Save"), name="save")
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        self.context.collective_immediatecreate = "created"
        # rename
        chooser = INameChooser(aq_parent(self.context))
        new_id = chooser.chooseName(None, self.context)
        api.content.rename(obj=self.context, new_id=new_id)
        api.portal.show_message(self.success_message, self.request)
        self.request.response.redirect(self.nextURL())
        notify(EditFinishedEvent(self.context))

    @button.buttonAndHandler(_dx(u"Cancel"), name="cancel")
    def handleCancel(self, action):
        api.portal.show_message(
            _dx(u"Add New Item operation cancelled"), self.request
        )
        self.request.response.redirect(self.nextURL())
        notify(EditCancelledEvent(self.context))
        parent = aq_parent(self.context)
        api.content.delete(obj=self.context)
        self.context = parent
        self.request.response.redirect(self.nextURL())

    def nextURL(self):
        view_url = self.context.absolute_url()
        portal_type = getattr(self, "portal_type", None)
        if portal_type is not None:
            registry = getUtility(IRegistry)
            use_view_action = registry.get(
                "plone.types_use_view_action_in_listings", []
            )
            if portal_type in use_view_action:
                view_url = view_url + "/view"
        return view_url

    def update(self):
        if (
            getattr(self.context, "collective_immediatecreate", None)
            != "initial"  # noqa: W503
        ):
            url = self.context.absolute_url() + "/edit"
            url = addTokenToUrl(url)
            raise Redirect(url)
        self.portal_type = self.context.portal_type
        super(ImmediateEditForm, self).update()

        # fire the edit begun only if no action was executed
        if len(self.actions.executedActions) == 0:
            notify(EditBegunEvent(self.context))

    def updateActions(self):
        super(ImmediateEditForm, self).updateActions()

        if "save" in self.actions:
            self.actions["save"].addClass("context")

        if "cancel" in self.actions:
            self.actions["cancel"].addClass("standalone")

    @property
    def fti(self):
        return getUtility(IDexterityFTI, name=self.portal_type)

    @property
    def label(self):
        type_name = self.fti.Title()
        return _(u"Add ${name}", mapping={"name": type_name})


ImmediateEditView = layout.wrap_form(ImmediateEditForm)
classImplements(ImmediateEditView, IDexterityEditForm)
