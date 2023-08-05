from dtpattern.alignment import utils

data=[
    ["fhttp://deri.org","https://deri.com"]
]




#data_list=[ [ c for c in s1]for s1 in data]





def symbol_to_patter(orig, symbol):

    m=[]

    for i, s in enumerate(symbol):
        if isinstance(s, str):
            m.append(s)
        elif isinstance(s, list):
            if len(s) == 1:
                # normally only happens if we compare two patterns with the same symbols
                m.append(s)
            elif len(s) != 2:
                print("WARNIGN {}".format(s))
            else:
                a1, a2 = s[0], s[1]

                if "-" in s:
                    opt=a2 if a1 =="-" else a1
                    if isinstance(opt,str):
                        opt=utils.translate(opt)
                    m.append((opt,0,1))

                else:
                    if isinstance(a1, str) and isinstance(a2, str):
                        # update vcounts
                        t = [utils.translate(a1), utils.translate(a2)]
                        m.append(list(set(t)))

                    if isinstance(a1, list) and isinstance(a2, str):
                        # we keep the a2 value in the freq dict,
                        # but need to merge the symbol
                        t = [utils.translate(a2)]
                        m.append(list(set(a1 + t)))
                    if isinstance(a1, str) and isinstance(a2, list):
                        # we keep the a2 value in the freq dict,
                        # but need to merge the symbol
                        t = [utils.translate(a1)]
                        m.append(list(set(a2 + t)))
    print("O:{} S:{}".format(orig, symbol))

    return m



def containsOpt(pattern):
    for c in pattern:
        if isinstance(c, tuple):
            return True
    return False

def expandOpt(pattern):
    exp=[]
    for c in pattern:
        if isinstance(c, tuple):
            exp +=[ (c[0]) for i in range(0,c[2])]
        else:
            exp.append(c)
    return exp

data_list=[
    [[c for c in 'http://deri.org/'],[c for c in 'https://deri.com']],
    [['1'],['1','0','1'],['1','1']]
]
for values in data_list:

    s1 = values[0]
    for s2 in values[1:]:

        _s1 = s1
        _s2 = s2
        #if containsOpt(s1):
        #    s1=expandOpt(s1)

        print("s1: {}\ns2: {}".format(s1,s2))

        #_p = merge_values("".join(s1), "".join(s2))
        #_s_p = pattern_to_string(_p, "".join(s1), "".join(s2))
        #print(_p,_s_p)
        from dtpattern.alignment import alignment_list as al
        als=al.align_global(s1,s2, 5, -4, -15, -1)
        print("Found {} alignment(s)".format(len(als)))
        for a in als:
            #print(al.format_alignment(*a))
            identity, score, align1, symbol, align2 = al.finalize(*a)

            print(al.format_alignment2(identity, score, align1, symbol, align2))

        #just take the first for now
        aa= al.finalize(*als[0])
        #print(al.format_alignment2(*aa))
        #print(aa[2])
        identity, score, align1, symbol, align2 = aa

        s1=symbol_to_patter(_s1,symbol)
        print("NEW: {}".format(s1))

        #for a in al.align.globalms(s1, s2, 5, -4, -15, -1):
        #    print(al.format_alignment(*a))

