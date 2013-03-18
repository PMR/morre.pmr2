import new

import zope.schema
import zope.interface
import zope.component


def buildMorreInterface(field_names, iface_name=None):
    """
    Take the list of available features and generate the required schema
    for the client form.
    """

    default = {
        '__module__': __name__,
        '__doc__': 'Dynamic interface for morre.pmr2.',
    }

    if iface_name is None:
        iface_name = 'IMorreFeatureSchema'

    fields = {}
    for c, field_name in enumerate(field_names):
        field = zope.schema.TextLine(
            title=field_name,
            required=False,
        )
        field.order = c
        # XXX validate the casting type.
        fields[str(field_name)] = field

    default.update(fields)

    interfaceClass = new.classobj(iface_name, (zope.interface.Interface,),
        default)

    return interfaceClass
