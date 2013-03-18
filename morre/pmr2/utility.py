import json
import requests

import zope.component
import zope.interface
from zope.schema.fieldproperty import FieldProperty

from persistent import Persistent
from zope.app.container.contained import Contained

from morre.pmr2.exc import MorreServerError
from morre.pmr2.interfaces import IMorreServer


class MorreServer(Persistent, Contained):
    zope.interface.implements(IMorreServer)

    server_uri = FieldProperty(IMorreServer['server_uri'])

    features = FieldProperty(IMorreServer['features'])

    # XXX these shold probably be editable.
    query_feature_endpoint = (
        '/db/data/ext/Diagnose/graphdb/cellml_model_query_features')
    query_endpoint = (
        '/morre/query/cellml_model_query')

    def __init__(self):
        pass

    def update(self):
        try:
            r = requests.post(
                self.server_uri + self.query_feature_endpoint)
            self.features = r.json()
        except:  # XXX should trap only requests specific exceptions
            # raising different exception
            raise MorreServerError()

    def getFeatures(self):
        return self.features

    def query(self, params):
        # TODO filter against self.features
        try:
            r = requests.post(
                self.server_uri + self.query_endpoint,
                data=json.dumps(params),
                headers={'content-type': 'application/json'},
            )
            result = r.json()
        except requests.exceptions.RequestException:
            # XXX raising different exception, hiding problem
            raise MorreServerError()

        return result
