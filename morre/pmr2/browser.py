import zope.component
from zope.component.hooks import getSiteManager

import z3c.form
from z3c.form import button

from Products.statusmessages.interfaces import IStatusMessage

from pmr2.z3cform import form

from morre.pmr2.exc import MorreServerError
from morre.pmr2.interfaces import IMorreServer
from morre.pmr2.utility import MorreServer
from morre.pmr2.schema import buildMorreInterface
from morre.pmr2.i18n import MessageFactory as _


class MorreAdminForm(form.EditForm):

    fields = z3c.form.field.Fields(IMorreServer).omit('features')
    serverFactory = MorreServer
    ignoreContext = True

    def getContent(self):
        result = zope.component.queryUtility(IMorreServer)
        return result

    def update(self):
        if self.getContent() is not None:
            self.ignoreContext = False
        super(MorreAdminForm, self).update()

    @button.buttonAndHandler(_('Install'), name='install')
    def handleInstall(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        changes = False
        server = self.getContent()
        if server is None:
            sm = getSiteManager()
            server = self.serverFactory()
            sm.registerUtility(server, IMorreServer)
            changes = True

        changes = self.applyChanges(data) or changes

        try:
            updated = server.update()

            if changes or updated:
                self.status = self.successMessage
            elif not self.status:  # only if this was not already applied.
                self.status = self.noChangesMessage

        except MorreServerError:
            self.status = _(u'There was a communication error with Morre.')

    @button.buttonAndHandler(_('Uninstall'), name='uninstall')
    def handleUninstall(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        server = self.getContent()
        if server is None:
            self.status = _(u'Server was not installed')
            return

        sm = getSiteManager()
        sm.unregisterUtility(server, IMorreServer)
        self.status = _(u'Server uninstalled')


class MorreSearchForm(form.PostForm):

    ignoreContext = True

    def acquireFeatures(self):
        server = zope.component.queryUtility(IMorreServer)
        if server is None:
            self.status = _('Morre server is not activated yet.')
            return []
        return server.getFeatures()

    def update(self):
        features = self.acquireFeatures()
        iface = buildMorreInterface(features)
        self.fields = z3c.form.field.Fields(iface)
        super(MorreSearchForm, self).update()

    @button.buttonAndHandler(_('Search'), name='search')
    def handleSearch(self, action):
        data, errors = self.extractData()
