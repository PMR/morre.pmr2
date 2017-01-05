import zope.component
import zope.interface
from zope.schema.fieldproperty import FieldProperty

from morre.pmr2.utility import MorreServer
from morre.pmr2.interfaces import IMorreServer
from morre.pmr2.exc import MorreServerError


class MockMorreServer(MorreServer):
    """
    This stubs out all the problematic methods that will do actual,
    real requests and replace certain methods to return the values that
    are expected.
    """

    server_uri = FieldProperty(IMorreServer['server_uri'])
    endpoints = FieldProperty(IMorreServer['endpoints'])

    features = {}
    _post_response = {}
    _last_post = None

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

    def _post(self, endpoint, data):
        self._last_post = {'endpoint': endpoint, 'data': data}
        if not isinstance(self._post_response, dict):
            raise MorreServerError
        return self._post_response

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

    def add_model(self, path, *a, **kw):
        # TODO actually move this to the test harness, mocking the
        # session or something.
        if 'error' in path:
            self._post_response = {u'errors': [{
                u'message': u'Some error happened',
                u'code': u'Neo.ClientError.Error'
            }]}
        elif 'exception' in path:
            self._post_reponse = None
        else:
            self._post_response = {'uID': '1'}
        return super(MockMorreServer, self).add_model(path, *a, **kw)
