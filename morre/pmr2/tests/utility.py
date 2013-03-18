import zope.component
import zope.interface
from zope.schema.fieldproperty import FieldProperty

from morre.pmr2.interfaces import IMorreServer


class MockMorreServer(object):
    zope.interface.implements(IMorreServer)

    server_uri = FieldProperty(IMorreServer['server_uri'])

    features = None

    _custom_features = False

    def __init__(self):
        pass

    def update(self):
        if self._custom_features is False:
            values = [u'NAME', u'ID', u'COMPONENT', u'VARIABLE', u'CREATOR',
                u'AUTHOR', u'URI']
        else:
            values = self._custom_features
        self.features = values
        return values is not None

    def getFeatures(self):
        return self.features

    def query(self, params):
        return []
