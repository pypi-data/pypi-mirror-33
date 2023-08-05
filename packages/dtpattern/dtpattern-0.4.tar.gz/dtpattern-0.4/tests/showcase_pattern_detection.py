
from csvmimesis.mimesis_data_providers import list_methods, list_locals, create_data, list_unique, \
    list_providers_methods
from csvmimesis.table_generator import create_data_provider_list

#print(list_methods())
from dtpattern.dtpattern1 import pattern

from dtpattern.timer import Timer


def print_columns(data, columns=4):

    my_len = len(data)
    my_len = (my_len - my_len % columns) + columns
    my_range = my_len // columns


    fin_list = [data[i * columns:i * columns + columns] for i in range(my_range)]


    sf="{:-^"+str(columns*31+1)+"}"
    print(sf.format(' DATA '))
    for item in fin_list:
        sf = len(item) * '|{:^30}'
        sf+="|"
        print(sf.format(*item))
    print((columns * 31+1) * '-')



def showcase_pattern(local=None, provider=None, method=None, size=10, seed="ascd", pattern1=True, pattern2=False, verbose=False):


    for l in list_locals():
        if not local or l==local:
            for pm in list_providers_methods( local=l, max_unqiue=size, only_max=True, seed=seed):
                p = "{}.{}".format(pm[0], pm[1])
                key="{}-{}".format(l,p)
                try:

                    header, data=create_data_provider_list(providers=[["{}".format(p),1]],  size=size, local=l, seed=seed)

                    data=data[header[0]]
                    data=[str(d) for d in data]

                    res=None
                    if pattern1:
                        with Timer(key="{}.{}-m1".format(key, size)) as t1:
                            res=pattern(data)

                    print("\n### {}  - {}".format(key, pm[2]))
                    if verbose:
                        print_columns(data, 6)
                    else:
                        print(" #=< {}".format(data))
                    print(" #=> {}".format(res))
                    #print(" TIMING: {}".format(Timer.printStats(keys=["{}.{}-m1".format(key, size)], header=False)))
                except Exception as e:
                    print(" #- {}  - {}".format(key, pm[2]))
                    print(" #=> {} {}".format(type(e).__name__, e))

    print(Timer.printStats(keys=['pattern1']))
    print(Timer.printStats())


showcase_pattern(local="de")
