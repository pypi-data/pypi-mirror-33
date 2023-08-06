# -*- coding: utf-8 -*-
"""
Created on Thu Jun  7 12:38:22 2018

@author: kferret061312
"""
import itertools
from IPython.display import display


class riskAnalysis:
    def __init__(self):
        self.dates = None
        self.forwards = None
        self.attr = ['dates', 'forwards']
        self.cartesian = False

    def make_list(self):
        att_l = self.attr.copy()
        for attr in att_l:
            att = getattr(self, attr)
            if att is not None:
                setattr(self, attr, att.split(','))
            else:
                self.attr.remove(attr)

    def longest_(self):
        assert 'dates' in self.attr, """ User has to set up at least one date """

        assert len(self.attr) == 2, """ User had to set up at least one forward shock"""
        ll = 0
        for attr in self.attr:
            l = len(getattr(self, attr))
            if l > ll:
                max_attr = attr
            ll = l
        self.longest = max_attr

    def cartesian_(self):

        longest = getattr(self, self.longest)
        attr_l = self.attr.copy()
        attr_l.remove(self.longest)
        if len(attr_l) > 2:
            prod_short = list(itertools.product(getattr(self, attr_l[0]), getattr(self, attr_l[1])))

            short_1 = [n[0] for n in prod_short]
            short_2 = [n[1] for n in prod_short]
            prod_1 = list(itertools.product(longest, short_1))
            prod_2 = list(itertools.product(longest, short_2))

            setattr(self, self.longest, [p[0] for p in prod_1])
            setattr(self, attr_l[0], [p[1] for p in prod_1])
            setattr(self, attr_l[1], [p[1] for p in prod_2])
        else:
            prod_1 = list(itertools.product(longest, getattr(self, attr_l[0])))
            setattr(self, self.longest, [p[0] for p in prod_1])
            setattr(self, attr_l[0], [p[1] for p in prod_1])

    def expand(self, verbose=False):
        self.make_list()

        if self.cartesian is True:
            self.longest_()
            self.cartesian_()
        else:
            assert self.forwards is not None, """ User has to set at least one forward shock"""
            # for i in self.attr[1:]:
            # assert len(getattr(self,self.attr[0])) == len(getattr(self,i)), """If
            # not a cartesian product then length of {} should be equal to length of {}""".format(self.attr[0],self.attr[1])

        self.riskAnalysis = {attr: getattr(self, attr) for attr in self.attr}

        if verbose is True:
            display(self.riskAnalysis)
