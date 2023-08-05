import functools
from statistics import mean

from dtpattern.pattern import substringFinder, sm_get_matching_blocks
from dtpattern.utils import sm_longest_match, sm_get_matching_blocks, substringFinder

str_pairs=[
    ("test","will"),
    ("https://deri.org", "http://deri.com"),
    ("https://deri.at", "http://wu.ac.at/"),
    ("http://.at", "http://wu.ac.at/"),
    ("ccccc://cccc.cc", "cccc://cc.cc.cc/"),
    ("ALISSA", "ALYSSA"),
    ("AT0001","AT0005"),
    ("aaabbb" ,"aabbb ")

]

func=[
substringFinder,
sm_get_matching_blocks,
sm_longest_match

]


_all_times={}
for s1,s2 in str_pairs:
    print(">> '{}' vs s2:{}".format(s1,s2))

    import timeit
    c=1


    times={}
    for cpf in func:
        print("  #{} -> {}".format(cpf.__name__, cpf(s1, s2)))
        t = timeit.Timer(functools.partial(cpf, s1, s2)).timeit(c)
        #print("  #{} ({}) {}".format(cpf.__name__,c,t))
        times[cpf.__name__]=t

    import operator
    sorted_times = sorted(times.items(), key=operator.itemgetter(1))
    fastest=sorted_times[0][1]
    print("   ->> Fastest algorithm: {} (over {} runs)".format(sorted_times[0][0],c))

    for k,v in sorted_times:
        print("    {} with {}, {}x slower than fastest".format(k,v, v/fastest))
        _all_times.setdefault(k,[])
        _all_times[k].append(v)


print()
for k,v in _all_times.items():
    print("{} min:{}, mean:{}, max:{}".format(k, min(v),mean(v),max(v)))



