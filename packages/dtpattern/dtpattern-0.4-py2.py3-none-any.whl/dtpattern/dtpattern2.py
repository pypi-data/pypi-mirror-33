import functools
import heapq
from enum import Enum
from operator import itemgetter
from dtpattern.alignment.merge import merge


from dtpattern.alignment.alignment_list import align_global,finalize, format_alignment2
from dtpattern.alignment import utils
from dtpattern.alignment.utils import indent
from dtpattern.timer import Timer, timer
import logging
logger = logging.getLogger(__name__)



@functools.total_ordering
class Pattern(object):

    @timer(key='patinit')
    def __init__(self, value:str, topk=3):
        self.symbol = [ c for c in value ]
        self._count = 1
        self.topk=topk
        self._vcounts = [ {c:1} for c in value ]

    def __eq__(self, other):
        if self._count == other._count:
            if len(self.symbol) == len(other.symbol):
                first_set = set(map(tuple, self.symbol))
                secnd_set = set(map(tuple, other.symbol))
                return first_set == secnd_set
        return False

    def __lt__(self, other):
        if self._count == other._count:
            if len(self.symbol) == len(other.symbol):
                return False
            else:
                return len(self.symbol) < len(other.symbol)
        else:
            return self._count < other._count

    def merge_with_pattern(self, p_beta, alignment):
        """ merge a pattern into this pattern based on the computed alignment
            in principle, this is the same as updating a pattern with an alignment,
            the only difference is the value counts of pattern beta
        """
        best_sym = alignment.best()['symbol']
        self.update_symbol(best_sym, beta_counts=p_beta._vcounts)
        self._count+=p_beta._count-1

    def update_with_alignment(self,alignment):
        if not isinstance(alignment, Alignment):
            raise ValueError("Method accepts only Alignment objects")

        best_sym=alignment.best()['symbol']
        self.update_symbol(best_sym)


    def update_counts(self, pos, value, cnt=None):
        return
        self._vcounts[pos].setdefault(value, 0)
        if cnt:
            self._vcounts[pos][value] += cnt
        else:
            self._vcounts[pos][value] += 1

        if len(self._vcounts[pos])>self.topk:
            d={k:v for k,v in heapq.nlargest(self.topk, self._vcounts[pos].items(), key=itemgetter(1))}
            #print(self._vcounts[pos],d)
            self._vcounts[pos]=d

    @timer(key='update_symbol')
    def update_symbol(self, symbol, beta_counts=None):
        logger.debug("[MERGE] Merging alignment {} into {}".format(symbol, self))
        m=[]

        if beta_counts is not None:
            pass

        a_i = 0
        b_i = 0
        for i, s in enumerate(symbol):
            if isinstance(s, str):
                #str means a character in both patterns
                m.append(s)
                self.update_counts(i,s) #update new mapping

                #if beta_counts and beta_counts[s]>1:
                #    self.update_counts(i, s, beta_counts[s]-1)

                a_i += 1
                b_i += 1


            elif isinstance(s, list):
                if len(s)==1:
                    #normally only happens if we compare two patterns with the same symbols
                    m.append(s)
                    #logger.debug("SINGLE VALUE {}".format(s))
                elif len(s)!=2:
                    logger.warning(" 0 or more than two elements in alignment list {}". format(s))
                else:
                    """
                    list -> means that we have one of the following cases:
                     1) s[0]:str and s[1]:str
                        => translate both elements and build the set
                    """
                    a1, a2 = s[0], s[1]

                    if '' in s:
                        if a1 == '':
                            # this is an insert, beta has an additional element
                            self._vcounts.insert(i, {None:0})
                            opt = a2
                            if isinstance(opt, str):
                                self.update_counts(i,opt)
                                #opt = utils.translate(opt)
                            elif isinstance(opt, tuple):
                                opt = opt[0]
                            m.append((opt, 0, 1))
                        else:
                            opt = a1
                            if isinstance(opt, tuple):
                                opt = opt[0]
                            m.append((opt, 0, 1))
                            self.update_counts(i, None)
                    else:
                        _m = merge(a1,a2)
                        m.append(_m)
                    # elif isinstance(a1, str) and isinstance(a2, str):
                    #     # update vcounts
                    #     t = [utils.translate(a1), utils.translate(a2)]
                    #     m.append(list(set(t)))
                    #     self.update_counts(i, a1)
                    #     self.update_counts(i, a2)
                    # elif isinstance(a1, list) and isinstance(a2, str):
                    #     # we keep the a2 value in the freq dict,
                    #     # but need to merge the symbol
                    #     t = [utils.translate(a2)]
                    #     m.append(list(set(a1 + t)))
                    #     self.update_counts(i, a2)
                    # elif isinstance(a1, str) and isinstance(a2, list):
                    #     # we keep the a2 value in the freq dict,
                    #     # but need to merge the symbol
                    #     t = [utils.translate(a1)]
                    #     m.append(list(set(a2 + t)))
                    # elif isinstance(a1, tuple) and isinstance(a2, str):
                    #     # we keep the a2 value in the freq dict,
                    #     # but need to merge the symbol
                    #
                    #     a10 = a1[0]
                    #     if isinstance(a1[0], list):
                    #         a10 = "".join(a10)
                    #     t = utils.translate(a2)
                    #     if t not in a10:
                    #         a10 += t
                    #
                    #     a1 = (a10, a1[1], a1[2])
                    #     m.append(a1)
                    #     self.update_counts(i, a2)
                    # elif  isinstance(a2, str):
                    #     logger.fatal("What is going on here")

        self.symbol = m
        self._count += 1
        logger.debug("[MERGED] Result of Merging alignment is: %s",self)

    @timer(key='_serialse')
    def _serialise(self):
        s=""
        _is_string=False
        for l in self.symbol:

            if isinstance(l,str):
                if not _is_string:
                    s+="'"
                    _is_string=True

            elif isinstance(l,list):
                if _is_string:
                    s += "'"
                    _is_string=False
                if len(l)==1:
                    s+=l[0]
                else:
                    _ps="".join(l)
                    s+="[{}]".format(_ps)

            elif isinstance(l,tuple):
                if _is_string:
                    s += "'"
                    _is_string=False
                #if l[2]==1:
                #    s += "{}*".format(l[0])
                #else:
                if isinstance(l[0], list):
                    sl = "[{0}]".format(','.join(map(str, l[0])))
                else:
                    sl = l[0]

                s += "{}{{{},{}}}".format(sl,l[1],l[2])

            if _is_string:
                s+=l

        if _is_string:
            s += "'"
        return s

    @timer(key='_compact')
    def _compact(self):

        it=iter(self.symbol)

        _s=''
        l=next(it, None)
        while l:
            try:
                _s_ = ""
                if isinstance(l,str):
                    _s_ ="'"
                    while True:
                        _s_+=l
                        l=next(it,None)
                        if not isinstance(l,str):
                            break

                    _s_+="'"
                elif isinstance(l,list):
                    _prev = l
                    _c=1
                    while True:
                        l=next(it,None)
                        if not isinstance(l,list):
                            break
                        if l == _prev:
                            _c+=1
                        else:
                            break
                    if len(_prev)==1:
                        if _c>1:
                            _s_ = "{}{}".format(_prev[0],_c)
                        else:
                            _s_ = "{}".format(_prev[0])
                    else:
                        _ps="".join(_prev)
                        _s_="[{}]".format(_ps)

                elif isinstance(l,tuple):
                    _prev = l
                    _c = 1
                    while True:
                        l = next(it,None)
                        if not isinstance(l, tuple):
                            break
                        if l == _prev:
                            _c += 1
                        else:
                            break
                        _prev=l
                    if _c ==1:
                        if isinstance(_prev[0], list):
                            if len(_prev[0])==1:
                                sl = "{0}".format(','.join(map(str, _prev[0])))
                            else:
                                sl = "[{0}]".format(','.join(map(str, _prev[0])))
                        else:
                            sl=_prev[0]
                        _s_ = "{}?".format(sl)
                    else:
                        if isinstance(_prev[0], list):
                            if len(_prev[0])==1:
                                sl = "{0}".format(','.join(map(str, _prev[0])))
                            else:
                                sl = "[{0}]".format(','.join(map(str, _prev[0])))
                        else:
                            sl=_prev[0]
                        _s_ = "{{{},{},{}}}".format(sl,_prev[1],_c)

                _s+=_s_
            except StopIteration:
                break

        return _s

    def __str__(self):
        return "{}(#{}): {} ( {} )".format('PAT',self._count, self._serialise(), self._compact())

    def __repr__(self):

        r=[
           ('list', self.symbol),
           ('string', self._serialise()),
           ('compact', self._serialise()),
            ('#freq', self._vcounts)

           ]

        s="\n#**-| {}(#values: {}): {} |-**".format(self.__class__.__name__, self._count, self._serialise())
        for k,v in r:
            s += "\n * {:<8} {}".format(k,v)

        s+="\n *-----"
        return s



class Alignment(object):

    @timer("Alignment_init")
    def __init__(self, alpha, beta, m=5, mm=-4, om=3, csetm=4,go=-15, ge=-1):

        self.alpha=alpha
        self.beta=beta
        self.data={}
        self.m=m
        self.mm=mm
        self.om=om
        self.go=go
        self.csetm=csetm
        self.ge=ge
        self.find_best_alignment( alpha.symbol, beta.symbol)

    def best(self):
        return self.data['best'] if 'best' in self.data else None

    def _translate(self,s):
        r = []
        for c in s:
            if isinstance(c, str):
                r.append([utils.translate(c)])
            elif isinstance(c, list):
                r.append(c)
        return r

    @timer(key='best_align')
    def find_best_alignment(self, alpha_list, beta_list):

        score_matrix={
            'match':self.m,
            'csetmatch':self.csetm,
            'optional_match':self.om,
            'mismatch': self.mm,
            'gapopen':self.go,
            'gapextend':self.ge
        }

        aligns=align_global(alpha_list, beta_list, **score_matrix)

        #TODO If we have several alignments, we might want to rank them on other features
        #if len(aligns)>1:
        #    import inspect
        #    logger.warning("MORE THAN ONE ALIGNMENT in {} {}".format(inspect.stack()[0][3], aligns))

        identity, score, align1, symbol2, align2 = finalize(*aligns[0])

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
                    if symbol2[i][0] != '':
                        if isinstance(symbol2[i][0],str):
                            ctrans = True
                            alpha_ct.append([utils.translate(symbol2[i][0])])
                        else:
                            alpha_ct.append(symbol2[i][0])
            if ctrans:
                aligns = align_global(alpha_ct, beta_list,match=self.m, csetmatch=self.m, mismatch=self.mm, gapopen=self.go, gapextend=self.ge)
                identity, score, align1, symbol2, align2 = finalize(*aligns[0])

                self.data['partl1'] = {
                    'score': score, 'identity': identity,
                    'align1': align1, 'align2': align2,
                    'symbol': symbol2
                }
        elif identity == 0:
            #no matching characters:

            alpha_ct = []
            for c in alpha_list:
                if isinstance(c,str):
                    alpha_ct.append([utils.translate(c)] )
                elif isinstance(c, tuple):
                    if isinstance(c[0], str):
                        alpha_ct.append(([utils.translate(c[0])], c[1],c[2]))
                    else:
                        alpha_ct.append(c)
                else:
                    alpha_ct.append(c)
            aligns = align_global(alpha_ct, beta_list, match=self.m, csetmatch=self.m, mismatch=self.mm, gapopen=self.go, gapextend=self.ge)
            #if len(aligns) == 1:
            #    import inspect
            #    logger.warning("MORE THAN ONE ALIGNMENT in {}".format(inspect.stack()[0][3]))
            identity, score, align1, symbol2, align2 = finalize(*aligns[0])

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
        s = "--ALIGNMENT: {} - {} --".format(repr(self.alpha), repr(self.beta))
        s += "\n costs: m:{} mm:{} go:{} ge:{}".format(self.m,self.mm,self.go,self.ge)
        for key, v in self.data.items():
            identity, score, align1, symbol, align2= v['identity'],v['score'],v['align1'],v['symbol'],v['align2']
            s+="\n {}\n{}".format(key,format_alignment2(identity, score, align1, symbol, align2, indent=2))

        return s

    def __str__(self):
        s="--ALIGNMENT({},{},{},{}): {} - {} --".format(self.m,self.mm,self.go,self.ge,self.alpha, self.beta)
        for key, v in self.data.items():
            identity, score, align1, symbol, align2= v['identity'],v['score'],v['align1'],v['symbol'],v['align2']
            s+=" \n[{:^8}] ident: {:6.2f} score: {:>3} SYM: {}".format(key, identity, score, symbol)

        return s

#def merge(pattern, alignment):
#
#    pattern.update_symbol(alignment.data['best']['symbol'])
#
#    return pattern


def compare(item1, item2):
    """
    compares first identity and if equals the score
    :param item1:
    :param item2:
    :return:
    """
    data1, data2 = item1[1], item2[1]
    if data1 is None and data2 is None:
        return 0
    elif data1 is None and data2 is not None:
        return -1
    elif data1 is not None and data2 is None:
        return +1
    else:
        res = data1.data['best']['identity'] - data2.data['best']['identity']
        if res == 0:
            res = data1.data['best']['score'] - data2.data['best']['score']
        return res


class CompressStrategy(Enum):
    ALL_AFTER=1

c_s={
    CompressStrategy.ALL_AFTER: "compress after a new pattern got created, compress all other pattern with 100% identity",

}

def compress_strategies():
    s=""
    for k,v in c_s.items():
        s+="{}: {}".format(k,v)
    return s


class PatternFinder(object):

    def __init__(self,max_pattern=1):
        self._max_patterns=max_pattern
        self._patterns = []
        self._count=0
        self._value_length=set([])
        self._char_count={}
        self.compress_strategy = CompressStrategy.ALL_AFTER

    def free_slots(self):
        return len(self._patterns)<self._max_patterns

    def add(self, value):
        logger.debug("{:-^30}".format(' ADD NEW '))
        logger.debug(" [%s] Adding value: %s", 'add', value)

        ivpat = Pattern(value)
        if self.free_slots():
            logger.debug(" We have free slots: adding empty pattern %s",ivpat)
            self._patterns.append( ivpat )
        else:
            logger.debug(" No free slots for %s", ivpat)

            #find closest pattern -> returns pos and alignment
            pos, alignment = self.closest_pattern_to(ivpat)
            logger.debug(" [BEST ALIGNMENT] Best alignment for %s is %s with ALIGN:%s", ivpat, self._patterns[pos], alignment.data['best'])
            if alignment.data['best']['identity'] != 100:
                # TODO: We need to decide at what stage we try to merge!!!
                cur_identity=alignment.data['best']['identity']
                self.compress_before(cur_identity)

                if self.free_slots():
                    logger.debug(" We have free slots after compressing: adding empty pattern %s", ivpat)
                    self._patterns.append(ivpat)
                    pos, alignment=None,None
                else:
                    logger.debug(" No free slots for %s", ivpat)

                    # find closest pattern -> returns pos and alignment
                    pos, alignment = self.closest_pattern_to(ivpat)
                    logger.debug(" Best alignment after compressing for input %s is for %s with ALIGN:%s", ivpat, self._patterns[pos],
                                 alignment.data['best'])

                #pass

            if pos is not None and alignment:
                p = self._patterns[pos]

                p.update_with_alignment(alignment)

                self.compress_after(pos)

        self._value_length.add(len(value))
        for c in value:
            self._char_count.setdefault(c,0)
            self._char_count[c]+=1
        self._count+=1
        logger.debug("--> %s", self)

    def compress_before(self, identity):
        """
        Try to compress the patterns before we insert a new one
        To do so, we need to compare the alignment between existing patterns.
        since alignments should be transitive, it should not matter if we do alpha-beta or beta-alpha

        rank the patterns based on their length

        :param identity:
        :return:
        """

        if len(self._patterns) == 1:
            logger.debug("[COMP_BEFORE] Only one pattern, Nothing to compress")
            return
        logger.debug("[COMP_BEFORE] Check if we can compress pattern groups with identiy >%s",identity)

        def compare_patterns(a,b):
            return len(a[1].symbol) - len(b[1].symbol)

        _s_al = sorted(enumerate(self._patterns), key=functools.cmp_to_key(compare_patterns), reverse=True)

        import itertools
        _al=[]
        _comb=[]
        for a, b in itertools.combinations(_s_al, 2):
            _comb.append((a[0],b[0]))
            alignment = Alignment(a[1], b[1])
            _al.append(alignment)


        _s_al = sorted(enumerate(_al), key=functools.cmp_to_key(compare), reverse=True)
        s=""
        for k in _s_al:
            s+="\n"+"  pos:{} {}".format(k[0],indent(k[1],5))
        logger.debug("[COMP_BEFORE] computed %s alignments %s", len(_s_al),s)


        best_align=_s_al[0][1]
        if best_align.best()['identity']>identity:
            a_idx, b_idx= _comb[_s_al[0][0]]
            p_alpha = self._patterns[a_idx]
            p_beta = self._patterns[b_idx]
            logger.debug("[COMP_BEFORE] We can merge two patterns %s %s",p_alpha, p_beta)


            p_alpha.merge_with_pattern(p_beta, best_align)
            self._patterns[a_idx] = p_alpha
            logger.debug("[COMP_BEFORE] Removing pattern at index %s %s", b_idx,self._patterns[b_idx])
            del (self._patterns[b_idx])


    def compress_after(self, idx):
        """
        call this function whenever a new merge was done.
        Check if any untouched pattern could be merged in the new pattern
        :return:
        """
        if len(self._patterns) == 1:
            logger.debug("[COMP] Only one pattern, Nothing to compress")
            return
        logger.debug("[COMP] Check if we can compress pattern groups")

        _al=[]
        _pat=self._patterns[idx]
        for i,_p in enumerate(self._patterns):
            if i != idx:
                #exclude idx
                alignment = Alignment(_pat, _p)
                _al.append(alignment)
            else:
                _al.append(None)


        _s_al = sorted(enumerate(_al), key=functools.cmp_to_key(compare), reverse=True)

        logger.debug("[COMP] Compared %s to %s patterns", _pat, len(_al))
        for k in _s_al:
            logger.debug(k[1])

        _idx, alignment = _s_al[0]

        logger.debug("[COMP] Best alignment for input %s is for %s with ALIGN:%s", _pat, self._patterns[_idx],
                     alignment.data['best'])
        id_to_del=[]
        for _idx, alignment in _s_al:
            if alignment and alignment.data['best']['identity'] == 100:

                p_alpha = self._patterns[idx]

                p_beta=self._patterns[_idx]
                p_alpha.merge_with_pattern(p_beta, alignment)
                self._patterns[idx] = p_alpha

                id_to_del.append(_idx)

        for i in sorted(id_to_del, reverse=True):
            logger.debug("[COMP_AFTER] Removing pattern at index %s %s", i, self._patterns[i])
            del (self._patterns[i])



    def closest_pattern_to(self, value, excludePos=None):
        """
        compuates the closest pattern, with closest as having the higest identiy or if equals highest score

        :param value: string value to add
        :param excludePos: optional parameter to exclude a certain existing pattern
        :return: position of closest pattern and the computed alignment
        """
        logger.debug("  >{:-^30}<".format(' CLOSEST PATTERN '))
        logger.debug("  Find closest pattern to %s (excludePos=%s)",value, excludePos)
        _al= []
        for i, _pat in enumerate(self._patterns):

            if excludePos is None or i != excludePos:
                alignment = Alignment( _pat, value)
                _al.append( alignment )
            else:
                _al.append(None)


        #sort, define sort function for alignment objects

        _s_al= sorted(enumerate(_al), key=functools.cmp_to_key(compare),reverse=True)


        s=""
        for k in _s_al:
            s+="\n"+indent(k[1],4)
        logger.debug("  Compared %s to %s patterns %s", value, len(_al),s)


        return _s_al[0]

    def info(self):
        s = "{:*>20} {} {:*<20}\n" \
            "  {:6>} elements\n" \
            " {:->2} {}/{} Groups {:-<10}".format("", self.__class__.__name__, "",
                                                  self._count,
                                                  "", len(self._patterns), self._max_patterns, "")
        c=0
        for i, p in enumerate(sorted(self._patterns, reverse=True)):
            s += "\n {:>2} {}".format(i, p)
            c+=p._count
        s+="\n -- sum: {}".format(c)
        return s



    def __str__(self):
        s="#{}[#{}, {}/{}]".format(self.__class__.__name__, self._count,len(self._patterns),self._max_patterns)

        for i,p in enumerate(sorted(self._patterns, reverse=True)):
            s+=" ${}-{} ".format(i,p)
        return s

    def __repr__(self):
        s = "\n#{:*>20} {} {:*<20}\n" \
            "#  {:6>} values added\n" \
            "# {:->2} {}/{} Groups {:-<10}".format("", self.__class__.__name__, "",
                                                  self._count,
                                                  "", len(self._patterns), self._max_patterns, "")
        for i, p in enumerate(sorted(self._patterns, reverse=True)):
            s += "\n# {:>2}: {}".format(i, repr(p))

        return s



@timer(key='pattern2')
def pattern(items, max_pattern=3):
    pm = PatternFinder(max_pattern=max_pattern)
    for value in items:
        pm.add(value)
    return pm





