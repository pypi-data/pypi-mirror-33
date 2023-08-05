
from dtpattern import debugConf, defaultConf, fileConf, infoConf
from dtpattern.dtpattern2 import PatternFinder, compress_strategies

from dtpattern.dtpattern2 import  pattern as pattern2
from dtpattern.dtpattern1 import pattern as pattern1


from dtpattern.timer import Timer, timer

import logging
import logging.config

from tests.bak.dtpattern2.mimesis_provider import create_data

logging.config.dictConfig(debugConf)
logger = logging.getLogger(__name__)


input_values=[str(i) for i in range(1,99)]
input_values=['http://deri.org/','https://deri.com']

data_lists=[
    (['111','222','Wien','Salzburg'],2),
    #(['1','WW','131W','ac123ac','cb-d-','http://'],2),
    #random_time(10),
    #random_iso8601(10),
    #random_date(10),
    #random_number(3,digits=3, fix_len=True),
    #random_isbn10(10),
    #random_isbn13(10),
    #random_word(100)
    #random_number(1000,digits=2, fix_len=False)
]



def get_patterns(d, groups):
    with Timer(factor=1000) as t:
        pm = PatternFinder(max_pattern=groups)
        logger.info("adding {} values (first 10: {} )".format(len(d),d[:10]))
        for value in d:
            logger.debug("->ADD {}".format(value))
            pm.add(value)
            logger.debug("<-ADD after adding value %s %s",value, pm)
            logger.debug(repr(pm))
        logger.info(pm)
        logger.info(repr(pm))
        logger.info(pm.info())

#for d,g in data_lists:
#    get_patterns(d,g)


def merge(data, max_patterns):
    print("groups:{} Sample {}".format(max_patterns,data[:15]))

    pm = PatternFinder(max_pattern=max_patterns)
    for value in data:
        pm.add(value)
        logger.debug(pm)
    #pm = pattern2(data, max_patterns)

    res = pattern1(data)
    print("## RESULTS ")
    print("  PAT-M1: {}".format(res))

    s = pm.info()
    s = "\n".join((3 * " ") + i for i in s.splitlines() if len(i.strip()) > 0)
    print("  PAT-M2:\n{}".format(s))

    print(Timer.printStats())

def test_mimesis_data(size=1000, provider='address', method='calling_code', max_patterns=3):
    mimesis_data_full=create_data(size=size, provider=provider, method=method)

    for k,v in mimesis_data_full.items():

        for sk,sv in v.items():

            if isinstance(sv[0], str):
                if len(sv[0])<15:

                    print("{:#>10} {:>15}.{:<15} {:#>10}\n## sample: {}".format('', k, sk, '',sv[0:25]))
                    with Timer(key="{}.{}-m2".format(k,sk)) as t2:
                        pm=pattern2(sv,max_patterns)

                    with Timer(key="{}.{}-m1".format(k, sk)) as t1:
                        res=pattern1(sv)
                    print("## RESULTS ")
                    print("  PAT-M1: {}".format(res))

                    s=pm.info()
                    s="\n".join((3 * " ") + i for i in s.splitlines() if len(i.strip())>0)
                    print("  PAT-M2:\n{}".format(s))
                    print("  TIMING: {}".format(Timer.printStats(keys=["{}.{}-m1".format(k, sk),"{}.{}-m2".format(k,sk)], header=False)))


    print(Timer.printStats())

test_mimesis_data(size=10, provider='address',  max_patterns=3, method=None)#,method='calling_code')

data=['Massachusetts', 'Florida', 'Delaware', 'New Hampshire', 'North Carolina', 'Arkansas', 'West Virginia', 'Ohio', 'Florida', 'Vermont']
merge(data, 2)
