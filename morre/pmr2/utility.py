import json
import logging
import requests

from BTrees.OOBTree import OOBTree

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
    portal_http_host = FieldProperty(IMorreServer['portal_http_host'])
    index_on_wfstate = FieldProperty(IMorreServer['index_on_wfstate'])

    features = FieldProperty(IMorreServer['features'])

    def __init__(self):
        # XXX uninstalling (via the form) will not clear this, nor does it
        # deindexes any data stored on that instance of morre.
        # TODO define behavior relating to that vs. this field.
        self.path_to_njid = OOBTree()

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

    def _post(self, endpoint, data):
        url = self.server_uri + endpoint
        jstr = json.dumps(data)
        try:
            r = requests.post(url, data=jstr, headers={
                'accept': 'application/json',
            })
            try:
                return r.json()
            except ValueError:
                logger.info('No json can be decoded from %s', url)
                return r.text
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

    def add_model(self, object_path,
                  portal_http_host=None, model_type='CELLML'):
        """
        Issue a call to add model to the morre database.

        Arguments:
        object_path
            path to the object to be added.
        portal_http_host
            The raw http host (not behind VHM) of the plone instance.
            Can be derived directly from request.get('HTTP_HOST'), which
            the installation form should have done.
        model_type
            Defaults to CELLML
        """

        if self.path_to_njid.get(object_path):
            # Don't add this again.
            return False

        if portal_http_host is None:
            portal_http_host = self.portal_http_host

        endpoint = '/morre/model_update_service/add_model'
        file_id = object_path.rsplit('/', 1)[-1]
        url = 'http://' + portal_http_host + object_path
        response = self._post(endpoint, data={
            'fileId': file_id,
            'url': url,
            'modelType': model_type,
        })

        self.path_to_njid[object_path] = response['uID']
        return True

    def del_model(self, object_path):
        """
        Issue a call to delete model from the morre database using the
        object_path
        """

        endpoint = '/morre/model_update_service/delete_model'
        uid = self.path_to_njid.get(object_path)

        if not uid:
            # did not delete anything.
            return False

        response = self._post(endpoint, data={
            'uID': uid,
        })

        self.path_to_njid.pop(object_path)

        # assume we got this
        return True
