# -*- coding: utf-8 -*-
from collective.preventactions import _
from collective.preventactions.interfaces import IPreventDelete
from collective.preventactions.interfaces import IPreventMoveOrRename
from plone.z3cform.layout import wrap_form
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form.browser.checkbox import SingleCheckBoxFieldWidget
from zope import schema
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.interface import noLongerProvides

import logging


logger = logging.getLogger('collective.preventeactions')


class PreventBool(schema.Bool):

    _type = bool

    def __init__(self, title, description, default, iface=None):
        super(PreventBool, self).__init__(
            title=title,
            description=description,
            required=False,
            default=default
        )
        self.iface = iface


class IPreventActions(Interface):
    """ Define form fields """

    delete = PreventBool(
        title=_(u'This object can not be deleted'),
        description=_(u'If check, this object can not be deleted.'),
        default=False,
        iface=IPreventDelete
    )

    move_or_rename = PreventBool(
        title=_(u'This object can not be moved or renamed'),
        description=_(
            u'If check, this object can not be moved or renamed (id).'),
        default=False,
        iface=IPreventMoveOrRename
    )


class PreventActionsForm(form.Form):
    fields = field.Fields(IPreventActions)
    label = _(u'Prevent actions')
    description = _(u'What actions will you prevent ?')
    fields['delete'].widgetFactory = SingleCheckBoxFieldWidget
    fields['move_or_rename'].widgetFactory = SingleCheckBoxFieldWidget

    def updateWidgets(self):
        """ Customize widget options before rendering the form. """
        super(PreventActionsForm, self).updateWidgets()

        # Dump out all widgets - note that each <fieldset> is a subform
        # and this function only concerns the current fieldset
        for widget_name in self.widgets:
            widget = self.widgets[widget_name]
            checked = widget.field.iface.providedBy(self.context)
            if checked:
                widget.value = [u'selected']
            else:
                widget.value = []

    @button.buttonAndHandler(_(u'Save'))
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        for name, value in data.items():
            if value:
                alsoProvides(self.context, self.fields[name].field.iface)
                self.widgets[name].value = [u'selected']
            else:
                noLongerProvides(self.context, self.fields[name].field.iface)
                self.widgets[name].value = []

        self.status = _(u'Changes saved')

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page.
        """


PreventActionsView = wrap_form(PreventActionsForm)
