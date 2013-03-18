import zope.interface
import zope.component

from zope.schema.interfaces import IVocabulary
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from pmr2.app.factory import vocab_factory

from morre.pmr2.interfaces import IMorreServer


class FeaturesVocab(SimpleVocabulary):

    zope.interface.implements(IVocabulary)

    def __init__(self, context=None):
        self.context = context
        terms = self._buildTerms()
        super(FeaturesVocab, self).__init__(terms)

    def _buildTerms(self):
        server = zope.component.queryUtility(IMorreServer)
        if server is None:
            return []
        features = sorted(server.getFeatures())
        terms = [SimpleTerm(i, i, i) for i in features]
        return terms

    def getTerm(self, value):
        try:
            return super(FeaturesVocab, self).getTerm(value)
        except LookupError:
            pass
        return SimpleTerm(None, None, value)

FeaturesVocabFactory = vocab_factory(FeaturesVocab)
