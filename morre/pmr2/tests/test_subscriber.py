import unittest
from unittest import TestSuite, makeSuite

from zope.component.hooks import getSiteManager
from zope.component import queryUtility
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.CMFCore.utils import getToolByName

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.layer import onsetup

from pmr2.app.exposure.content import ExposureFile

import morre.pmr2.tests.base
from morre.pmr2.tests.base import MorreExposureTestCase
from morre.pmr2.interfaces import IMorreServer
from morre.pmr2.tests.utility import MockMorreServer


class MorreSubscriberTestCase(MorreExposureTestCase):

    def setUp(self):
        super(MorreSubscriberTestCase, self).setUp()
        ef = ExposureFile('file')
        self.portal.exposure['1']['file'] = ef
        ef.reindexObject()

    def tearDown(self):
        server = queryUtility(IMorreServer)
        if server:
            sm = getSiteManager()
            sm.unregisterUtility(server, IMorreServer)

    def test_basic_workflow_no_server(self):
        # Make sure this doesn't crap out.
        self._publishContent(self.portal.exposure['1'])

    def test_basic_workflow_not_setup(self):
        # Make sure this doesn't crap out.
        sm = getSiteManager()
        server = MockMorreServer()
        sm.registerUtility(server, IMorreServer)
        self._publishContent(self.portal.exposure['1'])
        self.assertIsNone(server._last_post)

    def test_basic_workflow_not_indexed(self):
        # Make sure this doesn't crap out.
        sm = getSiteManager()
        server = MockMorreServer()
        server.index_on_wfstate = [u'pending']
        sm.registerUtility(server, IMorreServer)
        self._publishContent(self.portal.exposure['1'])
        self.assertIsNone(server._last_post)

    def test_basic_workflow_index_and_deindex(self):
        # Make sure this doesn't crap out.
        sm = getSiteManager()
        server = MockMorreServer()
        server.index_on_wfstate = [u'published']
        server.portal_http_host = u'127.0.0.1:8000'
        sm.registerUtility(server, IMorreServer)
        self._publishContent(self.portal.exposure['1'])
        self.assertEqual(server._last_post, {
            'endpoint': '/morre/model_update_service/add_model',
            'data': {
                'url': u'http://127.0.0.1:8000/plone/exposure/1/file',
                'modelType': 'CELLML',
                'fileId': 'file',
            },
        })

        # retract it
        pw = getToolByName(self.portal, "portal_workflow")
        self.setRoles(('Manager',))
        pw.doActionFor(self.portal.exposure['1'], "retract")
        self.setRoles(('Member', 'Authenticated',))

        self.assertEqual(server._last_post, {
            'endpoint': '/morre/model_update_service/delete_model',
            'data': {'uID': '1'}
        })


def test_suite():
    # explicitly defined to exclude the imported *TestCase classes.
    suite = TestSuite()
    suite.addTest(makeSuite(MorreSubscriberTestCase))
    return suite
