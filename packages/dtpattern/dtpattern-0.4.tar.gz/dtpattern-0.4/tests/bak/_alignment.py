from dtpattern import alignment
from dtpattern.alignment import alignment_orig
from dtpattern.merge import merge_values
from dtpattern.serialise import pattern_to_string
from dtpattern.utils import translate
from tests.bak import test_merge_same_csets

s1="1234"
s2="1234"

def test(s1,s2):
    print(s1,s2)
    align1, align2= alignment_orig.water(s1,s2)
    n_align1, n_align2 = alignment_orig.needle(s1, s2)

    res=[ (align1,align2), (n_align1,n_align2)]
    print(res)
    c=0
    for _align1, _align2 in res:
        c+=1
        print(c,_align1,_align2)

        identity, score, align1, symbol2, align2 = alignment_orig.finalize(_align1, _align2)
        print("{}\n{}\n{}".format(align1, "".join(symbol2), align2))
        print(" Identity {0:3.3f}%, Score:{1}".format(identity, score))
        print("-----")

for s1,s2,r in []:#test_merge_same_csets.data:
    s1, s2 = [c for c in s1], [c for c in s2]

    test(s1,s2)
    continue

    align1, align2= alignment2.water(s1,s2)
    n_align1, n_align2 = alignment2.needle(s1, s2)

    res=[(align1,align2), (n_align1,n_align2)]
    for align1,align2 in res:

        identity, score, align1, symbol, align2=alignment2.finalize(align1,align2)


        identity, score, align1, symbol2, align2 = alignment2.finalize2(align1, align2)

        print("-----")
        print("s1: {}".format(align1))
        print("    {}".format(symbol))
        print("s2: {}".format(align2))
        print(" Identity {0:3.3f}%, Score:{1}".format(identity,score))
        print("  sym:{}".format(symbol2))



data=[([c for c in "ATF12"],
       [c for c in "AT123"]),

       ([c for c in "ATCdddd"],
       [c for c in "ATddd"]),

      ([c for c in "12"],
       [c for c in "1235"]),


      #(['A','T',['C'],['c'],['c']],
       #['A', 'T', '1', 'g', 'h']),

      #(['A','T',['c'],['c','d'],['c']],
      # ['A', 'T', 'f', 'G', 'h'])
      ]

def align(s1,s2):
    """

    input is a  list of characters or character set symbols for each s1 and s2
    return is

    :param s1:
    :param s2:
    :return: tuple of align1, align2, symbol2, identity, score

    """
    _align1, _align2 = alignment_orig.needle_list(s1, s2)
    identity, score, align1, symbol2, align2 = alignment_orig.finalize2(_align1, _align2)

    return align1, align2, symbol2, identity, score


def print_alignment(align1, align2, symbol2, identity, score, altype="VALUE"):

    s="{:-^40}\n" \
      " s1: {}\n" \
      " s2: {}\n" \
      "  a: {}\n" \
      "  identity: {:2.2f}% Score: {}".format("ALIGNMENT "+altype,align1, align2, str(symbol2), identity, score)

    print(s)

def string_to_list(s):
    return [c for c in s]

def merge_alignment(symbol):
    m=[]
    for s in symbol:
        if isinstance(s,str):
            m.append(s)
        elif isinstance(s, list):
            a1=s[0]
            a2=s[1]
            #if isinstance(a1,list) and isinstance(a2, str):
                ##a1 is already a merge or optional


            t=set(translate("".join(s)))
            m.append([c for c in t])

    return m

def is_valid_alignment(align1, align2, symbol2):
    return True

def _translate(s):
    r=[]
    for c in s:
        if isinstance(c,str):
            r.append([translate(c)])
        elif isinstance(c, list):
            r.append(c)
    print(r)
    return r


data=[
    ["http://deri.org","https://deri.com"]
]






for values in data:

    s1 = values[0]
    for s2 in values[1:]:
        print("MERGE:\n\t{}\n\t{}".format(s1,s2))

        if isinstance(s1,str):
            s1= string_to_list(s1)
        if isinstance(s2,str):
            s2= string_to_list(s2)

        print(s1,s2)
        align1, align2, symbol2, identity, score = align(s1,s2)
        print_alignment(align1, align2, symbol2, identity, score)

        _s1,_s2=s1,s2
        if is_valid_alignment(align1, align2, symbol2):
            s1 = merge_alignment(symbol2)


        align1, align2, symbol2, identity, score = align(_translate(_s1), _s2)
        print_alignment(align1, align2, symbol2, identity, score, altype="TRANS")
















        if True:
            print(_s1,_s2)
            #_p = merge_values("".join(s1), "".join(s2))
            #_s_p = pattern_to_string(_p, "".join(s1), "".join(s2))
            #print(_p,_s_p)
            from dtpattern.alignment import alignment as al
            for a in al.align.globalms("".join(_s1), "".join(_s2), 5, -4, -15, -1):
                print(al.format_alignment(*a))

#<class 'list'>: [[0, -50, -100, -150, -200], [-50, 5, -45, -95, -145], [-100, -45, 10, -40, -90], [-150, -95, -40, 15, -35]]
#<class 'list'>: [[0, -50, -100, -150, -200], [-50, 5, -45, -95, -145], [-100, -45, 10, -40, -90], [-150, -95, -40, 15, -35]]
