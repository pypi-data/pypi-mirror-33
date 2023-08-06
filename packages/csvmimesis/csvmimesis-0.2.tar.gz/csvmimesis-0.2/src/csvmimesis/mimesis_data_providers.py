import inspect
from mimesis import Generic
from mimesis.config import SUPPORTED_LOCALES


def list_locals():
    return [k for k in SUPPORTED_LOCALES]

def print_locals():
    for l in list_locals():
        print(l)

def list_providers():
    generic = Generic()
    return [str(c) for c in dir(generic)]

def list_methods(providers=None):
    if providers is None:
        providers = list_providers()
    elif not isinstance(providers, list):
        providers = [providers]


    methods={}
    generic = Generic()
    for c in providers:

        for cc in inspect.getmembers(getattr(generic,c), predicate=inspect.ismethod):
            if not cc[0].startswith("_"):
                m=methods.setdefault(str(c),[])
                m.append(str(cc[0]))
    return methods


def show_mimesis():
    for p,ms in list_methods().items():
        for m in ms:
            print("{}.{}".format(p, m))


def print_mimesis(provider=None):
    for p,ms in list_methods(providers=provider).items():
        print("{:=^80}".format(p.center(len(p) + 2)))
        for m in ms:
            print(" * {}".format(m))


def print_unique(provider=None, method=None, local=None, max=1000):
    data = create_data(max_unique=max, local=local, provider=provider, method=method)
    for k, v in data.items():
        print("{:=^80}".format(k.center(len(k)+2)))
        for kk, vv in v.items():
            print(" * {:>20} {}".format(kk, vv))
def list_unique(provider=None, method=None, local=None, max=1000):
    data = create_data(max_unique=max, local=local, provider=provider, method=method)
    result=[]
    for k, v in data.items():
        for kk, vv in v.items():
            result.append((k,kk))
    return result

def create_data(local=None, provider=None, method=None, max_unique=100, seed=None):
    generic = Generic(local, seed=seed)
    data={}
    for c in dir(generic):
        if not provider or provider == c:
            data[c]={}
            for cc in inspect.getmembers(getattr(generic,c), predicate=inspect.ismethod):
                if not cc[0].startswith("_"):
                    if not method or method == cc[0]:
                        d=set([])
                        max_tries=100
                        a = 0
                        try:
                            while len(d)<max_unique:
                                value = cc[1]()
                                if value not in d:
                                    d.add(value)
                                    a=0
                                else:
                                    a += 1
                                if a > max_tries:
                                    break
                        except Exception:
                            pass
                        data[c][cc[0]]=len(d)
    return data

def print_providers(data=None, local=None, max_unqiue=10000, only_max=False):

    max_unique = max_unqiue
    data = data if data else create_data(max_unique=max_unique, local=local)
    for k, v in data.items():
        for kk, vv in v.items():
            if not only_max or vv == max_unique:
                print("{:>15}.{:<15} {}".format(k, kk, vv))

def list_providers_methods(data=None, local=None, max_unqiue=10000, only_max=False, seed=None):
    max_unique = max_unqiue
    d=[]
    data = data if data else create_data(max_unique=max_unique, local=local, seed=seed)
    for k, v in data.items():
        for kk, vv in v.items():
            if not only_max or vv == max_unique:
                d.append( (k,kk,vv))
    return d


