# -*- coding: utf-8 -*-





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
