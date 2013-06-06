import json
import logging
import requests

import zope.component
import zope.interface
from zope.schema.fieldproperty import FieldProperty

from persistent import Persistent
from zope.container.contained import Contained

from morre.pmr2.exc import MorreServerError
from morre.pmr2.interfaces import IMorreServer

logger = logging.getLogger('morre.pmr2.utility')


class MorreServer(Persistent, Contained):
    zope.interface.implements(IMorreServer)

    server_uri = FieldProperty(IMorreServer['server_uri'])
    endpoints = FieldProperty(IMorreServer['endpoints'])

    features = FieldProperty(IMorreServer['features'])

    def __init__(self):
        pass

    def _loadFeature(self, endpoint):
        url = self.server_uri + endpoint
        try:
            r = requests.get(url, headers={
                'accept': 'application/json',
            })
            try:
                return r.json()
            except:
                logger.info('No json can be decoded from %s', url)
                # TODO subclass a more appropriate error.
                raise MorreServerError()
        except requests.exceptions.RequestException:
            logger.info('Error while trying to access %s', url, exc_info=1)
            return MorreServerError()

    def update(self):
        self.features = {}
        error = None
        for endpoint in self.endpoints:
            try:
                feature = self._loadFeature(endpoint)
            except MorreServerError as e:
                # don't overwrite the first error.
                if error is None:
                    error = e
                continue
            self.features[endpoint] = feature

        # raise the deferred exception.
        if error:
            raise error

        return bool(self.features)

    def getFeatures(self, end_point):
        if self.features:
            return self.features.get(end_point, [])
        return []

    def getAllFeatures(self):
        if self.features:
            return self.features
        return {}

    def query(self, end_point, params):
        # TODO filter against self.features
        url = self.server_uri + end_point
        data = json.dumps(params)
        try:
            r = requests.post(url, 
                data=data,
                headers={
                    'accept': 'application/json',
                    'content-type': 'application/json',
                },
            )
            try:
                result = r.json()
            except:
                logger.info('No json can be decoded from %s, data was %s',
                    url, data)
                raise MorreServerError()
        except requests.exceptions.RequestException as e:
            logger.error('Exception raised:', exc_info=1)
            raise MorreServerError()

        return result
