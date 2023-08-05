from dtpattern.alignment import needle

data=[
    ("http://deri.org/", "https://deri.com")
]

def _biopy(s1,s2):
    from dtpattern.alignment import alignment as al
    for a in al.align.globalms(s1, s2, 5, -4, -15, -1):
        print(a)
        print(al.format_alignment(*a))

def _align4(s1,s2):
    from dtpattern.alignment._align4 import affine_gap
    sequ1r, sequ2r, score = affine_gap(s1,s2)
    print("Sequence 1: ", sequ1r)
    print("Sequence 2: ", sequ2r)
    print("Score     : ", score)


def _needle(s1,s2):
    identity, score, align1, symbol, align2 = needle(s1,s2)
    print(align1)
    print(align2)
    print(score)

for s1, s2 in data:

    print("-- {}\n"
          "-- {}".format(s1,s2))

    _align4(s1,s2)
    _biopy(s1,s2)
    _needle(s1,s2)
