import functools

from contexttimer import Timer

from dtpattern.alignment import needle, finalize
from dtpattern.utils import translate


class Pattern(object):

    def __init__(self, value:str):
        self.value = value
        self.symbol=None
        self._count = 1
        self._vcounts=None

    def to_list(self):
        if self.symbol:
            return [c for c in self.symbol]
        return [c for c in self.value]

    def merge_alignment(self,symbol):
        m = []
        for s in symbol:
            if isinstance(s, str):
                m.append(s)
            elif isinstance(s, list):
                a1 = s[0]
                a2 = s[1]
                # if isinstance(a1,list) and isinstance(a2, str):
                ##a1 is already a merge or optional


                t = set(translate("".join(s)))
                m.append([c for c in t])

        return m

    def update_symbol(self, symbol):
        #TODO length check
        m=[]
        if not self._vcounts:
            self._vcounts=[{} for i in range(0,len(symbol))]

        for i, s in enumerate(symbol):
            if isinstance(s, str):
                m.append(s)
            elif isinstance(s, list):
                if len(s)==1:
                    #normally only happens if we compare two patterns with the same symbols
                    m.append(s)
                    print("SINGLE VALUE {}".format(s))
                elif len(s)!=2:
                    print("WARNIGN {}". format(s))
                else:
                    a1 = s[0]
                #
                    a2 = s[1]

                    if isinstance(a1, str) and isinstance(a2, str):
                        #
                        self._vcounts[i].setdefault(a1,0)
                        self._vcounts[i].setdefault(a2, 0)
                        self._vcounts[i][a1]+=1
                        self._vcounts[i][a2] += 1
                        t = [translate(a1), translate(a2)]

                        m.append(list(set(t)))

                    if isinstance(a1,list) and isinstance(a2, str):
                        #we keep the a2 value in the freq dict,
                        # but need to merge the symbol
                        t = [translate(a2)]
                        m.append(list(set(a1+t)))
        self.symbol=m
        self._count+=1



    def merge_value(self, value, alignment):
        """

        :param value: the string value
        :param alignment: the already computated default alignment
        :return:
        """
        #here we do the whole merge of a value

    def _serialise(self):
        s=""
        _is_string=False
        for l in self.to_list():

            if isinstance(l,str):
                if not _is_string:
                    s+="'"
                    _is_string=True

            if isinstance(l,list):
                if _is_string:
                    s += "'"
                    _is_string=False

                if len(l)==1:
                    s+=l[0]
                else:
                    _ps="".join(l)
                    s+="["+_ps+"]"

                #s+=str(l)

            if _is_string:
                s+=l

        if _is_string:
            s += "'"
        return s

    def __str__(self):
        return "{}(#{}): {}".format(self.__class__.__name__,self._count, self._serialise())

    def __repr__(self):
        return "{}(#{}): \n   {}\n   {}\n   {}".format(self.__class__.__name__, self._count, self.value,self.symbol, self._vcounts)



def to_list(alpha):
    if isinstance(alpha, str):
        return [c for c in alpha]

    if isinstance(alpha, Pattern):
        return alpha.to_list()

    #if isinstance()

    #if isinstance(alpha, str) and isinstance(beta, str):
    #    self.string_alignment(alpha, beta)
    #elif isinstance(alpha, Pattern) and isinstance(beta, str):
    #    self.pattern_string_alignment(alpha, beta)
    #elif isinstance(alpha, str) and isinstance(beta, Pattern):
    #    self.pattern_string_alignment(beta, alpha)
    #elif isinstance(alpha, Pattern) and isinstance(beta, Pattern):
    #    self.pattern_alignment(alpha, beta)


class Alignment(object):

    def __init__(self, alpha, beta):

        self.data={}

        alpha_list = to_list(alpha)
        beta_list = to_list(beta)

        self.find_best_alignment( alpha_list, beta_list)

    def _translate(self,s):
        r = []
        for c in s:
            if isinstance(c, str):
                r.append([translate(c)])
            elif isinstance(c, list):
                r.append(c)

        return r
    def find_best_alignment(self, alpha_list, beta_list):

        identity, score, align1, symbol2, align2 = needle(alpha_list, beta_list)
        self.data['raw']={
            'score':score, 'identity':identity,
            'align1':align1,'align2':align2,
            'symbol':symbol2
        }
        if 0< identity < 100:
            ctrans=False
            #translate the non matching symbols in alpha
            alpha_ct=[]
            for i in range(0, len(align1)):
                if len(symbol2[i])==1:
                    alpha_ct.append(align1[i])
                else:
                    if symbol2[i][0] != '-':
                        if isinstance(symbol2[i][0],str):
                            ctrans = True
                            alpha_ct.append([translate(symbol2[i][0])])
                        else:
                            alpha_ct.append(symbol2[i][0])
            if ctrans:
                identity, score, align1, symbol2, align2 = needle(alpha_ct, beta_list)
                self.data['partl1'] = {
                    'score': score, 'identity': identity,
                    'align1': align1, 'align2': align2,
                    'symbol': symbol2
                }
        elif identity == 0:
            #no matching characters:

            identity, score, align1, symbol2, align2 = needle(self._translate(alpha_list), beta_list)
            self.data['l1'] = {
                'score': score, 'identity': identity,
                'align1': align1, 'align2': align2,
                'symbol': symbol2
            }



        if len(self.data)>1:
            def compare(item1, item2):
                res = item1[1]['identity'] - item2[1]['identity']
                if res == 0:
                    res = item1[1]['score'] - item2[1]['score']
                return res

            _s_al = sorted(enumerate(list(self.data.values())), key=functools.cmp_to_key(compare))
            self.data['best'] = _s_al[-1][1]
        else:
            self.data['best'] = self.data['raw']

    def __repr__(self):
        return "{}".format(self.data)

def merge(pattern, alignment):
    pattern.update_symbol(alignment.data['best']['symbol'])

    return pattern



class PatternFinder(object):

    def __init__(self,max_pattern=1):
        self._max_patterns=max_pattern
        self._patterns = []
        self._count=0

    def add(self, value):
        #


        if len(self._patterns)<self._max_patterns:
            self._patterns.append(Pattern(value))
        else:
            #find closest pattern
            idx, alignment = self.closest_pattern_to(value)

            if alignment.data['best']['identity'] != 100:
                print("Check if we can merge patterns")

            p = self._patterns[idx]

            print("  Adding pattern, best: {}".format(alignment.data['best']))

            p = merge( p , alignment)
            self._patterns[idx]=p


            #TODO, define compress process
            self.compress(idx)

        self._count+=1

    def compress(self, idx):
        """
        call this function whenever a new merge was done.
        Check if any untouched pattern could be merged in the new pattern
        :return:
        """
        for i,_p in enumerate(self._patterns):
            if i != idx:
                _idx, alignment = self.closest_pattern_to(_p, exclude=i)

                if _idx == idx:
                    if alignment.data['best']['identity'] == 100:
                        p = self._patterns[idx]

                        p = merge(p, alignment)
                        p._count+=self._patterns[i]._count-1
                        self._patterns[idx] = p
                        print("match")
                        self._patterns.pop(i)




    def closest_pattern_to(self, value, exclude=None):

        _al= []
        for i,_p in enumerate(self._patterns):
            if  exclude is None or i !=exclude:
                alignment = Alignment(_p,value)
                _al.append( alignment)
            else:
                _al.append(None)


        #sort, define sort function of alignment objects

        def compare(item1, item2):
            if item1[1] is None and item2[1] is None:
                return 0
            elif item1[1] is None and item2[1] is not None:
                return -1
            elif item1[1] is not None and item2[1] is None:
                return +1
            else:
                res= item1[1].data['best']['identity'] - item2[1].data['best']['identity']
                if res == 0:
                    res = item1[1].data['best']['score'] -item2[1].data['best']['score']
                return res
        _s_al= sorted(enumerate(_al), key=functools.cmp_to_key(compare))


        return _s_al[-1]

    def __str__(self):
        s="{:*>20} {} {:*<20}\n" \
          "  {:6>} elements\n" \
          " {:->2} {}/{} Groups {:-<10}".format("",self.__class__.__name__,"",
                            self._count,
                            "",len(self._patterns),self._max_patterns,"")
        for i,p in enumerate(self._patterns):
            s+="\n {:>2}: {}".format(i,p)

        return s

    def __repr__(self):
        s = "{:*>20} {} {:*<20}\n" \
            "  {:6>} elements\n" \
            " {:->2} {}/{} Groups {:-<10}".format("", self.__class__.__name__, "",
                                                  self._count,
                                                  "", len(self._patterns), self._max_patterns, "")
        for i, p in enumerate(self._patterns):
            s += "\n {:>2}: {}".format(i, repr(p))

        return s



pm= PatternFinder(max_pattern=1)

input_values=[str(i) for i in range(1,99)]
input_values=['http://deri.org/','https://deri.com']

with Timer(factor=1000) as t:
    for value in input_values:
        #print("\nADDING {}".format(value))
        pm.add(value)
        #print(pm)
        #print(repr(pm))
print("{} ms".format(t.elapsed))

print(pm)








