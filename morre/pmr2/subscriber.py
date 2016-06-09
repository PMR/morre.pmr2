import zope.component

from Products.CMFCore.utils import getToolByName
from morre.pmr2.interfaces import IMorreServer


def get_exposure_files(obj):
    c = getToolByName(obj, name='portal_catalog')
    path = '/'.join(obj.getPhysicalPath())
    # XXX configurable way that filter by CellML
    return (p.getPath() for p in c(portal_type='ExposureFile', path=path))


def create_handler(checker, method):
    def handler(obj, event):
        ms = zope.component.queryUtility(IMorreServer)
        if not ms or not event.transition:
            return

        if not checker(event.transition.new_state_id,
                       ms.index_on_wfstate or []):
            return

        for p in get_exposure_files(obj):
            getattr(ms, method)(p)

    return handler

add_to_morre = create_handler(
    lambda state, states: state in states, 'add_model')
del_from_morre = create_handler(
    lambda state, states: state not in states, 'del_model')
