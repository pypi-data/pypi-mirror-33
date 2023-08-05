import functools
from time import sleep

from dtpattern.pattern import Pattern

str_pairs=[
    #("test","will"),
    #("https://deri.org", "https://test.com"),
    #("https://deri.at", "http://wu.ac.at/"),
    #("http://.at", "http://wu.ac.at/"),
    #("ccccc://cccc.cc", "cccc://cc.cc.cc/"),
    #("ALISSA", "ALYSSA"),
    #("AT0001","AT0005"),
    #("aaabbb" ,"aabbb ")

]

for s1,s2 in str_pairs:
    p = Pattern(s1)
    print(repr(p))

    _in = Pattern(s2)
    print(repr(_in))

    p.merge(_in)

    print(repr(_in))
    print(_in)
    sleep(2)





