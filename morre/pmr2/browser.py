import json
from urlparse import urlparse

import zope.component
from zope.component.hooks import getSiteManager
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

import z3c.form
from z3c.form import button
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from plone.z3cform.fieldsets import extensible

from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName

from pmr2.z3cform import form

from morre.pmr2.exc import MorreServerError
from morre.pmr2.interfaces import IMorreServer, IMorreSearchForm
from morre.pmr2.interfaces import IMorreSearchFormLayer
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
        http_host = self.request.get('HTTP_HOST', '127.0.0.1')

        # a hacky way to override one-off values without plunging into
        # the whole persistent registration framework.
        self.request['form.widgets.portal_http_host'] = unicode(http_host)

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
            self.status = _(u'There were errors with the update; '
                'details can be found in server logs.')

    @button.buttonAndHandler(_('Uninstall'), name='uninstall')
    def handleUninstall(self, action):
        data, errors = self.extractData()
        if errors:
            # No real need to check errors as the content is being
            # removed
            pass

        server = self.getContent()
        if server is None:
            self.status = _(u'Server was not installed')
            return

        sm = getSiteManager()
        sm.unregisterUtility(server, IMorreServer)
        self.status = _(u'Server uninstalled')


class MorreSearchGroup(form.PostForm, form.Group):

    ignoreContext = True

    @button.buttonAndHandler(_('Search'), name='search')
    def handleSearch(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        # TODO fix the schema so that tokens are pre-split into a list
        features = []
        keywords = []
        for k, v in data.iteritems():
            if not v:
                continue
            features.append(k)
            keywords.append(v)

        if features:
            self.parentForm.target = self.endpoint
            if 'keyword' in features:
                # if the features is just keywords, don't pass that in
                # but just join all the keywords together.
                self.parentForm.query = {
                    'keyword': ' '.join(keywords),
                }
            else:
                self.parentForm.query = {
                    'features': features,
                    'keywords': keywords,
                }


class MorreSearchForm(form.PostForm, extensible.ExtensibleForm):

    ignoreContext = True
    template = ViewPageTemplateFile('morre_search_form.pt')

    results = None
    result_count = 0

    def __init__(self, *a, **kw):
        super(MorreSearchForm, self).__init__(*a, **kw)
        self.fields = z3c.form.field.Fields()

        self.target = self.query = None

    def getContent(self):
        server = zope.component.queryUtility(IMorreServer)
        if server is None:
            self.status = _('Morre server is not activated yet.')
            return None
        return server

    def acquireFeatures(self):
        server = self.getContent()
        if server:
            return server.getAllFeatures()
        return {}

    def update(self):
        zope.interface.alsoProvides(self.request, IMorreSearchFormLayer)
        self.appendGroups()
        # buttons triggered here.
        extensible.ExtensibleForm.update(self)

        # the activated action will set the target and query to make.
        server = self.getContent()
        if not self.target or not server:
            return

        # Only attempt to query if both target and server are present.
        try:
            results = server.query(self.target, self.query)
        except MorreServerError as e:
            self.status = _(u'There was a problem executing this query.')
            return

        if not results:
            # nothing.
            return

        if isinstance(results[0], basestring):
            # assume fail somewhere (no results most likely)
            return

        self.processResults(results)

    def processResults(self, raw_results):
        """
        """

        server = self.getContent()
        results = []
        catalog = getToolByName(self.context, 'portal_catalog')
        portal_url = getToolByName(self.context, 'portal_url')

        for result in raw_results:
            # XXX here we have the assumption of where the file actually
            # is.

            try:
                subpath = urlparse(result['documentURI']).path
            except KeyError:
                # not an exposure result, append as is
                results.append(result)
                continue

            brains = catalog(path=subpath)
            if not brains:
                continue

            brain = brains[0]

            if brain.pmr2_review_state != 'published':
                # must be published (i.e. not expired).
                continue

            result['documentURI'] = brain.getURL()

            # XXX based on the old school items
            result['modelName'] = brain.pmr1_citation_authors
            result['modelDescription'] = brain.pmr1_citation_title
            results.append(result)

        self.results = results
        self.result_count = len(self.results)

    def appendGroups(self):
        self.groups = []
        features = self.acquireFeatures()
        for endpoint, names in features.iteritems():
            iface = buildMorreInterface(names)
            grp = MorreSearchGroup(self.context, self.request, self)
            key = endpoint.split('/')[-1]

            grp.label = key
            grp.endpoint = endpoint
            grp.fields = z3c.form.field.Fields(iface)
            grp.prefix = str(key)
            self.groups.append(grp)
