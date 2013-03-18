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
