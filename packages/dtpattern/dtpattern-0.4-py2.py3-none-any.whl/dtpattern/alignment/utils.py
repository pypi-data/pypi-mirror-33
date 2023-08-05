import itertools
import string
from difflib import SequenceMatcher as SM

UPPER = 'C'
LOWER = 'c'
DIGIT = 'd'
SPECIAL = '$'
BRACKET = 'ß'
in_out2 = {
    string.digits: DIGIT,
    string.ascii_lowercase: LOWER,
    string.ascii_uppercase: UPPER,
    'äöü': LOWER,
    'ÄÖÜ': UPPER,
    ' ': ' ',
}


def make_trans_table_unicode(in_out):
    translate_table = {}
    for i, o in in_out.items():
        for char in i:
            translate_table[ord(char)] = str(o)

    return translate_table


all_table_unicode = make_trans_table_unicode(in_out2)


def translate(input, trans_table=all_table_unicode):
    ''' use the unicode mapping'''
    if type(input) != str:
        input = input.decode('utf-8')
    return input.translate(trans_table)


def unique_order(seq):

    return ''.join([x[0] for x in itertools.groupby(seq)])


def indent(s, indent):
    return "\n".join((indent * " ") + i for i in str(s).splitlines())

def sm_longest_match(s1,s2):
    """
    Uses the difflib SequenceMatcher to find common sub patterns
    1) find longest pattern,
    2) replace the longest pattern with "" in both string
    3) repeat 1
    :param s1:
    :param s2:
    :return: an ordered list containing the longest common subsequences, ordered by length
    """
    anslist=[]
    match = SM(None, s1, s2).find_longest_match(0, len(s1), 0, len(s2))
    match_pat = s1[match.a: match.a + match.size]
    while match.size > 1:
        anslist.append( (match_pat, match.a) )

        #replace match pattern from string
        s1=s1.replace(match_pat,'')
        s2 = s2.replace(match_pat, '')

        match = SM(None, s1, s2).find_longest_match(0, len(s1), 0, len(s2))

        match_pat = s1[match.a: match.a + match.size]

    return anslist


def sm_get_matching_blocks(s1,s2,min_length=1):
    """
    Uses the difflib SequenceMatcher to find all common sub patterns
    :param s1:
    :param s2:
    :return: a list of common subpatterns, starting from strings
    """
    anslist= list(SM(None, s1, s2).get_matching_blocks())


    anslist = [ l for l in anslist if l.size>=min_length]

    anslist=[ (s1[l.a:l.a+l.size], l.a, l.b, l.size) for l in anslist]
    return anslist


def substringFinder(string1, string2):
    """

    :param string1:
    :param string2:
    :return: a list of matchign substrings, can contain overlapping strings
    s1 = "aaabbb"
    s2 = "aabbb"
    substringFinder(s1,s2)
    ['aa', 'bb', 'aabbb', 'bb']
    """
    answer = ""
    anslist=[]
    len1, len2 = len(string1), len(string2)
    for i in range(len1):
        match = ""
        for j in range(len2):
            if (i + j < len1 and string1[i + j] == string2[j]):
                match += string2[j]
            else:
                #if (len(match) > len(answer)):
                answer = match
                if answer != '' and len(answer) > 1:
                    anslist.append(answer)
                match = ""

        if match != '':
            anslist.append(match)
        # break
    return anslist
