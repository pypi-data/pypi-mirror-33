import itertools


from dtpattern.merge import merge_values
from dtpattern.utils import sm_get_matching_blocks, translate, unique_order

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)-8s - %(name)s - %(message)s  ')


######## Common sequence algrotihm

class Pattern(object):
    def __init__(self, value=None):
        self.count=1
        self._reset()

    def _reset(self):
        self._values = []
        self._l1patterns = []
        self._l2patterns = []
        self._rep_ = []
        self._l2string = None
        self._l1string = None
        self._l2string = None


    def parse_value(self, value):
        logger.debug("CREATE PATTERN")
        if not value:
            return

        t = translate(value)

        logger.debug("{:>2} translated:{}".format('',t))
        #o=unique_order(t)
        #logger.debug("O:{}".format(o))
        l1_grouped = [(k, sum(1 for i in g)) for k, g in itertools.groupby(t)]
        logger.debug("{:>2} L1-groups:{}".format('',l1_grouped))

        c=0
        for g in l1_grouped:
            self._l2patterns.append((g[0],c,g[1]))
            self._l1patterns.append(t[c:c+g[1]])
            self._values.append(value[c:c + g[1]])
            c+=g[1]

        self._l2string= "".join([p[0] for p in self._l2patterns])
        self._l1string = "".join(self._l1patterns)
        self._valuestring = "".join(self._values)

    def value_string(self):
        return self._valuestring

    @classmethod
    def from_value(cls,valueString):
        _p=Pattern()
        _p.parse_value(valueString)
        return _p

    @classmethod
    def from_string(cls,pstring):

        _p= Pattern()
        ins=''
        parseValue=True
        valuestring=''
        for c in pstring:
            if c == "'":
                if not parseValue:
                    #start
                    parseValue=True
                else:
                    #end
                    _p._values.append(valuestring)
                    _p._l1patterns.append(translate(valuestring))
                    parseValue=False
            else:
                if parseValue:
                    valuestring+=c
                else:
                    pass







    def merge_pattern(self, toMerge):
        #check if we have only values

        if all( isinstance(elem, str) for elem in self._values) and all( isinstance(elem, str) for elem in toMerge._values):
            _merge_pattern = merge_values(self._valuestring, toMerge._valuestring)
            print (_merge_pattern)

            self._reset()

            for _p in _merge_pattern:
                if isinstance(_p,str):
                    self.parse_value(_p)
                elif isinstance(_p,list):
                    pass






        if self._valuestring == toMerge._valuestring:
            # ok we have the same value strings

            #1
            if not self.aggregated and not toMerge.aggregated:
                # both pattern are plain
                # do nothing and increment count
                self.count+=1
            else:
                #TODO value strings are the same, now we need to check the other patterns
                pass
        else:
            # different strings, lets check for common substrings
            value_blocks = sm_get_matching_blocks(self._valuestring, toMerge._valuestring)
            logger.debug("MatchingBlocks: {}".format(value_blocks))



            #if len(value_blocks)!=0:
                #
                #for
                ## ok, we have at least one common substring which we want to preserve

            #find out which L2


        l2_grouped_agg = []
        for k, g in itertools.groupby([self._l2string,toMerge._l2string], lambda x: unique_order(x)):
            g = [i for i in g]  # we need to get this since groupby gives an iterator which can be exhausted
            l2_grouped_agg.append((k, len(g), g))
        print(l2_grouped_agg)
        #if len(l2_grouped_agg):

    def merge(self, value):
        """ simple helper function
        if the input is not a pattern object, then create one"""
        if not isinstance(value, Pattern):
            value = Pattern(value)
        self.merge_pattern(value)

#### representation ####
    def __repr__(self):
        s="*----- Pattern\n" \
          "* L2: {}\n" \
          "* L1: {}\n" \
          "*  V: {}\n" \
          "*  count:{}\n" \
          "*-----".format(self._l2patterns, self._l1patterns, self._values, self.count)
        return s

    def __str__(self):
        s = "PATTERN ".format(self.count)
        for i, v in enumerate(self._values):
            if v is not None:
                s+="'{}'".format(v)
        return s+" (freq:{})".format(self.count)


