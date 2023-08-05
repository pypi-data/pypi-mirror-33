from csvmimesis.mimesis_data_providers import list_methods, list_locals, create_data, list_unique, \
    list_providers_methods
from csvmimesis.table_generator import create_data_provider_list

#print(list_methods())
from dtpattern.dtpattern1 import pattern

from tests import print_columns


def pattern1(provider, size, local, seed):
    try:
        header, data=create_data_provider_list(providers=[[provider,1]],  size=size, local=local, seed=seed)

        data=data[header[0]]
        data=[str(d) for d in data]

        p=pattern(data)

        print("#- {} - {}".format(provider, local))

        print_columns(data, 6)
        print("#=> {}".format(p[0]))
    except Exception as e:
        print("#- {} - {}".format(provider, local))
        print("#=> {} {}".format(type(e).__name__, e))


size=10
seed="asdf"
local="de"
provider="address.address"

pattern1(provider=provider, size=size, seed=seed, local=local)

