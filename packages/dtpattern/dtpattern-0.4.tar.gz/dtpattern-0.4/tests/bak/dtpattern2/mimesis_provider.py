from mimesis import Generic


g = Generic('en')


data=[g.person.height(), g.person.weight()]
#print(data)

#print(g)
#print(dir(g))

def create_data(generic=Generic('en'), size=10, provider=None, method=None):
    import inspect
    data={}
    for c in dir(generic):
        if not provider or provider==c:
            data[c]={}
            for cc in inspect.getmembers(getattr(generic,c), predicate=inspect.ismethod):
                if not cc[0].startswith("_"):
                    if not method or cc[0]==method:
                        data[c][cc[0]]=[cc[1]() for i in range(0,size)]
    return data



#read http://mimesis.readthedocs.io/api.html#usual-data-providers



def cities(size):
    return [ g.address.city() for i in range(0,size)]

def postal_codes(size):
    return [g.address.postal_code() for i in range(0, size)]

def zip_code(size):
    return [g.address.zip_code() for i in range(0, size)]

def make_mimessis_data(size, provider):
    return [provider() for i in range(0, size)]

#print(zip_code(10))
#print(make_mimessis_data(10,g.code.isbn))
