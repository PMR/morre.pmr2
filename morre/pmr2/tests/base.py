import zope.component
import zope.interface
from zope.annotation.interfaces import IAttributeAnnotatable

from Testing import ZopeTestCase as ztc
from plone.session.tests.sessioncase import PloneSessionTestCase
from Zope2.App import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.layer import onsetup
from Products.PloneTestCase.layer import onteardown

from pmr2.app.exposure.tests.base import CompleteDocTestCase


@onsetup
def setup():
    import morre.pmr2
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', morre.pmr2)
    fiveconfigure.debug_mode = False

@onteardown
def teardown():
    pass

setup()
teardown()
ptc.setupPloneSite()


class MorreExposureTestCase(CompleteDocTestCase):
    """
    Base test case class, we want a complete environment here.
    """
