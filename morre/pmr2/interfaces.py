import zope.interface

from z3c.form.interfaces import IFormLayer
from plone.app.z3cform.interfaces import IPloneFormLayer


class IMorreServer(zope.interface.Interface):
    """
    Interface for the morre server
    """

    server_uri = zope.schema.TextLine(
        title=u'Server Location',
        description=u'Root URL to the target Morre server',
        default=u'http://127.0.0.1:7474',
    )

    portal_http_host = zope.schema.TextLine(
        title=u'Portal HTTP Host',
        description=u'The true host of server behind http. This value is set'
                     'automatically, please select install to finalize.',
        default=u'',
    )

    endpoints = zope.schema.List(
        title=u'Endpoints',
        description=u'Paths to the valid query endpoints on that server',
        value_type=zope.schema.TextLine(),
    )

    features = zope.schema.Dict(
        title=u'Cached Features',
        required=False,
        key_type=zope.schema.TextLine(),
        value_type=zope.schema.List(),
    )

    def update():
        """
        Query the server for an updated list of available features.
        """

    def getFeatures():
        """
        Return the list of features.
        """


class IMorreSearchForm(zope.interface.Interface):

    keywords = zope.schema.TextLine(
        title=u'Keywords',
        description=u'A list of keywords, separated by whitespace.',
    )

    features = zope.schema.List(
        title=u'Features',
        description=u'Features to query with',
        required=False,
        value_type=zope.schema.Choice(vocabulary='morre.pmr2.features'),
    )


class IMorreSearchFormLayer(IFormLayer):
    pass
