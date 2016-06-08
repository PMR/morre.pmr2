import zope.component

from Products.CMFCore.utils import getToolByName
from morre.pmr2.interfaces import IMorreServer


def get_exposure_files(obj):
    c = getToolByName(obj, name='portal_catalog')
    path = '/'.join(obj.getPhysicalPath())
    # XXX configurable way that filter by CellML
    return (p.getPath() for p in c(portal_type='ExposureFile', path=path))


def add_to_morre(obj, event):
    ms = zope.component.getUtility(IMorreServer)

    if event.transition.new_state_id not in ms.index_on_wfstate:
        return

    for p in get_exposure_files(obj):
        ms.add_model(p)


def del_from_morre(obj, event):
    ms = zope.component.getUtility(IMorreServer)

    if event.transition.new_state_id in ms.index_on_wfstate:
        return

    for p in get_exposure_files(obj):
        ms.del_model(p)
