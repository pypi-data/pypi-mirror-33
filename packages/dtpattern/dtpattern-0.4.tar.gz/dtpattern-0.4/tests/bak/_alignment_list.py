
data=[
    ["fhttp://deri.org","https://deri.com"]
]




#data_list=[ [ c for c in s1]for s1 in data]


data_list=[
    [ [['d']] ,['1','0','1']]
]


for values in data_list:

    s1 = values[0]
    for s2 in values[1:]:

        print(s1,s2)

        #_p = merge_values("".join(s1), "".join(s2))
        #_s_p = pattern_to_string(_p, "".join(s1), "".join(s2))
        #print(_p,_s_p)
        from dtpattern.alignment import alignment_list as al
        for a in al.align_global(s1,s2, 5, -4, -15, -1):
            print(al.format_alignment(*a))
            identity, score, align1, symbol, align2 = al.finalize(*a)

            print(al.format_alignment2(identity, score, align1, symbol, align2))

        #for a in al.align.globalms(s1, s2, 5, -4, -15, -1):
        #    print(al.format_alignment(*a))

