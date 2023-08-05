
##debug
import unittest


from dtpattern.merge import merge_values
from dtpattern.serialise import pattern_to_string
from dtpattern.pattern import sm_get_matching_blocks, Pattern
from dtpattern.utils import translate, sm_get_matching_blocks
import logging

from tests import for_examples

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
data=[
    ("ATcde",
     "ATfgh",    "'AT'c{3}"),

    ("ATcde",
     "ATfg",    "'AT'c{2,3}"),

    ("dATcde",
     "eATfg",    "c{1}'AT'c{2,3}"),

    ("aBCdEF",
     "eBCfEF",    "c{1}'BC'c{1}'EF'"),

    ("aBCdEF",
     "eBCfEFe",    "c{1}'BC'c{1}'EF'c{0,1}"),

    ("abCD",
     "efCD",    "c{2}'CD'"),

    ("1234",
     " 234",    "d{0,1}'234'"),

    ("1234",
     " 244",    "d{3,4}"),

    ("12016123",
     "20161233", "d{8}"),

    ("12016123",
     "201612323", "d{8,9}"),

    ("https",
     "http", "'http'c{0,1}"),

    ("AT123",
     "ATC23", "'http'c{0,1}"),
]

value_pattern_data=[
    (("https","http") , "http")
]




#for s1,s2,r in data:
#    d = alignment.align.localxx(s1, s2)#

#    alignment2.needle(s1,s2)
#    print(s1,s2,r)
#    print("alginment: {}".format(d))


class TestOneCharSet(unittest.TestCase):



    @for_examples(data)
    def test_value_merge(self, s1, s2,r):

        logger.info("INPUT  {} {}".format(s1, s2))
        _p = merge_values(s1, s2)

        _s_p = pattern_to_string(_p, s1, s2)
        _s_p_full = pattern_to_string(_p, s1, s2, full_string=True)


        logger.info(" >>P: {} => {} or {}".format(_p, _s_p, _s_p_full))
        self.assertEqual(_s_p,r)












