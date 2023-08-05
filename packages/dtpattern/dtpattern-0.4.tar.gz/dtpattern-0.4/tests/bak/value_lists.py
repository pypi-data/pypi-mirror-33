from tests.bak.value_pattern_types_list import random_number, random_lowercase_string, random_date, random_uppercase_string

test_cols_aggregated=[
    ( random_number(2,digits=1, fix_len=True)+random_number(2,digits=2, fix_len=True), '01'),
    (random_date(5), '1111-11-11'),
    #(random_time(5), '11:11:11'),
    #(random_iso8601(5), '1111-11-11C11:11:11'),
    (random_lowercase_string(10, length=5),'ccccc'),
    (random_lowercase_string(5, length=5)+random_lowercase_string(5, length=3),'aaccc'),
    #(random_word(10,length=5),'Ccccc'),
    #(random_word(5,length=5)+random_word(5,length=3),'Caacc'),
    #(random_words(10,length=[5,3]),'Ccccc Ccc'),
    #(random_words(5,length=[5,3])+random_words(5,length=[3,5]),'Caacc Caacc'),
]

def number_map(l=10, count=10):
    return { i:random_number(l, digits=i, fix_len=True) for i in range(1,count) }

same_length_numbers  =[ (number_map()[i], '1'*i) for i in range(1,5) ]
same_length_lowercase=[ (random_lowercase_string(10, length=i), 'c'*i) for i in range(1,5) ]
same_length_uppercase=[ (random_uppercase_string(10, length=i), 'C'*i) for i in range(1,5) ]

def rndtuple(n=10, m=5):
    from random import randint
    for i in range(1,n):
        a,b=randint(1,m),randint(1,m)
        yield (min(a,b), max(a,b))



var_length_numbers=[
    (random_number(3, digits=t[0], fix_len=True)+random_number(3, digits=t[1], fix_len=True), '0'*(t[1]-t[0])+'1'*t[0])
    for t in rndtuple(100)
]
var_length_lowercase=[
    (random_lowercase_string(10, length=t[0])+random_lowercase_string(10, length=t[1]),'a'*(t[1]-t[0])+'c'*t[0])
    for t in rndtuple(100)
]
var_length_uppercase=[ (random_uppercase_string(10, length=i), 'C'*i) for i in range(1,5) ]


#This cases are not that straight forward
test_cols_aggregated_complex=[
    ( [u'-1']+random_number(5,digits=1, fix_len=True), '[-]1'), # sometimes numbers contain a minus
    ( [u'-1',u'+1']+random_number(5,digits=1, fix_len=True), '[-/+]1')
]
