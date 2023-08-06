# -*- coding: utf-8 -*-
from ..utils import itemgetter


class MyStemAnalysis(object):

    def __init__(self, analysis_):
        self._analysis = analysis_

    def __iter__(self):
        return zip(self.texts(), self.analyses())

    def analyses(self):
        return map(itemgetter('analysis', []), self._analysis)

    def texts(self):
        return map(itemgetter('text', ''), self._analysis)
