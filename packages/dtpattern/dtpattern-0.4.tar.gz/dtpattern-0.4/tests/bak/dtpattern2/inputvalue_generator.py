import string

from faker import Factory
fake = Factory.create('en_GB')

### some providers
def make_pattern(size, f, **fargs):
    return [str(f(**fargs)) for i in range(0, size)]

def random_time(size, pattern="%H:%M:%S"):
    return make_pattern(size, fake.time, pattern=pattern)

def random_iso8601(size):
    return make_pattern(size, fake.iso8601, tzinfo=None)

def random_date(size, pattern="%Y-%m-%d"):
    return make_pattern(size, fake.date, pattern=pattern)

def random_number(size, digits=None, fix_len=False):
    return make_pattern(size, fake.random_number, digits=digits, fix_len=fix_len)

def random_lowercase_string(size, length=10):
    return make_pattern(size, fake.random_number, elements=(string.ascii_lowercase),length=length)


def random_uppercase_string(size, length=10):
    return make_pattern(size, fake.random_number, elements=(string.ascii_uppercase), length=length)

def random_word(size, length=10):
    return [str(''.join(fake.random_sample(elements=(string.ascii_uppercase), length=1)))+str(''.join(fake.random_sample(elements=(string.ascii_lowercase), length=length-1))) for i in
            range(0, size)]

def random_isbn13(size, separator='-'):
    return make_pattern(size, fake.isbn13, separator=separator)

def random_isbn10(size, separator='-'):
    return make_pattern(size, fake.isbn10, separator=separator)
