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
    ...     'form.widgets.endpoints': u'/morre/query/cellml_model_query\n'
    ...                                '/morre/query/person_model_query',
    ...     'form.buttons.install': 1,
    ... })
    >>> view = MorreAdminForm(self.portal, request)
    >>> view.serverFactory = MockMorreServer
    >>> 'features' not in view.fields.keys()
    True
    >>> result = view()
    >>> view.status
    u'Data successfully updated.'

The workflow, along with the active host should be registered to the,
object also::

    >>> ms = view.getContent()
    >>> ms.portal_http_host
    u'127.0.0.1'

Now the search form should be rendered::

    >>> request = TestRequest()
    >>> view = MorreSearchForm(self.portal, request)
    >>> result = view()
    >>> 'Morre server is not activated yet.' in result
    False
    >>> len(view.groups)
    2
    >>> view.groups[0].prefix
    'cellml_model_query'
    >>> view.groups[0].fields.keys()
    ['NAME', 'ID', 'COMPONENT', 'VARIABLE', 'CREATOR', 'AUTHOR', 'URI']
    >>> view.groups[1].prefix
    'person_model_query'
    >>> view.groups[1].fields.keys()
    ['EMAIL', 'FAMILYNAME', 'GIVENNAME']

Try to query against this form::

    >>> request = TestRequest(form={
    ...     'cellml_model_query.widgets.NAME': u'model name',
    ...     'cellml_model_query.widgets.ID': u'model id',
    ...     'cellml_model_query.buttons.search': 1,
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
