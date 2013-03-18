Morre Demo Server Interface
===========================

Set up the imports::

    >>> import zope.component
    >>> from pmr2.testing.base import TestRequest
    >>> from morre.pmr2.browser import MorreSearchForm
    >>> from morre.pmr2.interfaces import IMorreServer

First try to render the query view without anything registered::

    >>> request = TestRequest()
    >>> view = MorreSearchForm(self.portal, request)
    >>> result = view()
    >>> 'Morre server is not activated yet.' in result
    True
    >>> 'VARIABLE' in result
    False

Activate the server::

    >>> from morre.pmr2.tests.utility import MockMorreServer
    >>> from morre.pmr2.browser import MorreAdminForm
    >>> request = TestRequest(form={
    ...     'form.widgets.server_uri': u'http://127.0.0.1:7474',
    ...     'form.buttons.install': 1,
    ... })
    >>> view = MorreAdminForm(self.portal, request)
    >>> view.serverFactory = MockMorreServer
    >>> 'features' not in view.fields.keys()
    True
    >>> result = view()
    >>> view.status
    u'Data successfully updated.'

Now the search form should be rendered::

    >>> request = TestRequest()
    >>> view = MorreSearchForm(self.portal, request)
    >>> result = view()
    >>> 'Morre server is not activated yet.' in result
    False
    >>> 'VARIABLE' in result
    True

Try to query against this form::

    >>> request = TestRequest(form={
    ...     'form.widgets.NAME': u'model name',
    ...     'form.widgets.ID': u'model id',
    ...     'form.buttons.search': 1,
    ... })
    >>> view = MorreSearchForm(self.portal, request)
    >>> result = view()
    >>> data, errors = view.extractData()

Deactivate the server::

    >>> request = TestRequest(form={
    ...     'form.widgets.server_uri': u'http://127.0.0.1:7474',
    ...     'form.buttons.uninstall': 1,
    ... })
    >>> view = MorreAdminForm(self.portal, request)
    >>> result = view()
    >>> view.getContent() is None
    True
