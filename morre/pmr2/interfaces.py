import zope.interface


class IMorreServer(zope.interface.Interface):
    """
    Interface for the morre server
    """

    server_uri = zope.schema.TextLine(
        title=u'Server Location',
        description=u'Root URL to the target Morre server',
        default=u'http://127.0.0.1:7474',
    )

    features = zope.schema.List(
        title=u'Cached Features',
        required=False,
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
