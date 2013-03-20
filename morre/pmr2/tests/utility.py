import zope.component
import zope.interface
from zope.schema.fieldproperty import FieldProperty

from morre.pmr2.interfaces import IMorreServer


class MockMorreServer(object):
    zope.interface.implements(IMorreServer)

    server_uri = FieldProperty(IMorreServer['server_uri'])
    endpoints = FieldProperty(IMorreServer['endpoints'])

    features = {}

    _custom_features = False
    _demo = {
        '/morre/query/cellml_model_query': [
            u'NAME', u'ID', u'COMPONENT', u'VARIABLE', u'CREATOR',
            u'AUTHOR', u'URI',
        ],
        '/morre/query/person_model_query': [
            u"EMAIL", u"FAMILYNAME", u"GIVENNAME",
        ],
    }

    def __init__(self):
        pass

    def update(self):
        self.features = {}
        for endpoint in self.endpoints:
            self.features[endpoint] = self._demo.get(endpoint, [])
        return bool(self.features)

    def getAllFeatures(self):
        return self.features

    def getFeatures(self, end_point):
        return self.features.get(end_point, [])

    def query(self, end_point, params):
        return []
