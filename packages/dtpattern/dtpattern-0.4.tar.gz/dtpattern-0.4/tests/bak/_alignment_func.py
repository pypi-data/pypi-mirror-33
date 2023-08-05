from dtpattern import alignment
from dtpattern.alignment import needle, finalize, gap_penalty, match_award, mismatch_penalty, water
from dtpattern.utils import translate

from dtpattern.alignment import alignment as al

def to_list(alpha):
    if isinstance(alpha, str):
        return [c for c in alpha]

def _translate(s):
    r=[]
    for c in s:
        if isinstance(c,str):
            r.append([translate(c)])
        elif isinstance(c, list):
            r.append(c)
    return r

def align(s1,s2):
    """

    input is a  list of characters or character set symbols for each s1 and s2
    return is

    :param s1:
    :param s2:
    :return: tuple of align1, align2, symbol2, identity, score

    """

    identity, score, align1, symbol2, align2 = needle(s1, s2)
    print_alignment(align1, align2, symbol2, identity, score, altype="NEEDLE")

    identity, score, align1, symbol2, align2 = water(s1, s2)
    print_alignment(align1, align2, symbol2, identity, score, altype="WATER")

    score_matrix = {
        gap_penalty: -15,
        match_award: 5,
        mismatch_penalty: -4
    }
    identity, score, align1, symbol2, align2 = needle(s1, s2,score_matrix=score_matrix)
    print_alignment(align1, align2, symbol2, identity, score, altype="VALUE")

    identity, score, align1, symbol2, align2 = water(s1, s2,score_matrix=score_matrix)
    print_alignment(align1, align2, symbol2, identity, score, altype="WATER")

    identity, score, align1, symbol2, align2 = needle(_translate(s1), s2)
    print_alignment(align1, align2, symbol2, identity, score, altype="TRANS")

    identity, score, align1, symbol2, align2 = water(_translate(s1), s2)
    print_alignment(align1, align2, symbol2, identity, score, altype="TRANS_WATER")


    #for a in al.align.globalms("".join(s1), "".join(s2), 5, -4, -50, -.1):
    #    print(al.format_alignment(*a))

    return align1, align2, symbol2, identity, score


def print_alignment(align1, align2, symbol2, identity, score, altype="VALUE"):

    s="{:-^40}\n" \
      " a1: {}\n" \
      " a2: {}\n" \
      "  s: {}\n" \
      "  identity: {:2.2f}% Score: {}".format("ALIGNMENT "+altype,align1, align2, str(symbol2), identity, score)

    print(s)

def is_valid_alignment(align1, align2, symbol):

    print("a1_len:{}, a2_len:{}, s_len:{}".format(len(align1), len(align2), len(symbol)))
    return True


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


data=[
    ['111',"1222","1113"]
]


for values in data:

    s1 = values[0]
    for s2 in values[1:]:
        print("MERGE:\n\t{}\n\t{}".format(s1,s2))

        if isinstance(s1,str):
            s1= to_list(s1)
        if isinstance(s2,str):
            s2= to_list(s2)


        align1, align2, symbol2, identity, score = align(s1,s2)
        #print_alignment(align1, align2, symbol2, identity, score)

        _s1,_s2=s1,s2
        while not is_valid_alignment(align1, align2, symbol2):
            break

        s1 = merge_alignment(symbol2)
