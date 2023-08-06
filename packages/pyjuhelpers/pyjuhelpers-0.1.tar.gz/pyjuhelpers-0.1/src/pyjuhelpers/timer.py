#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals



from io import StringIO
from operator import itemgetter
from statistics import mean
import numpy
__author__ = 'jumbrich'
import collections
import functools
import time


class Timer(object):
    GLOBAL_VERBOSE=True
    measures={}

    def __init__(self,  key=None, verbose=False, store=True):
        self.verbose = verbose
        self.key=key
        self.store=store

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        end = time.time()
        secs = end - self.start
        msecs = secs * 1000  # millisecs
        if self.verbose and Timer.GLOBAL_VERBOSE:
            print('(%s) elapsed time: %f ms' % (self.key,msecs))
        if self.key and self.store:
            if self.key not in self.__class__.measures:
                self.__class__.measures[self.key]=[]
            if msecs>=0:
                self.__class__.measures[self.key].append(msecs)

    @classmethod
    def printStats(cls, key=None, keys=None, header=True, sort_key=[7]):

        h1 = "\n {:^30} {:^5} {:^10} {:^10} {:^10} {:^10} {:^10} {:^10}".format("method",'count','min','q25','avg','q75','max','sum')
        l_s= len(h1)
        l="\n {:-^"+str(l_s)+"}"
        l = l.format("")
        s=""
        data=cls.getStatsAsLists()
        data=sorted(data, key=itemgetter(*sort_key), reverse=True)
        for row in data:
            m=row[0]
            if (key is None and  keys is None) or (key and m== key) or (keys and m in keys):
                _s_="\n {:>30} {:>5} {:>10.3f} {:>10.3f} {:>10.3f} {:>10.3f} {:>10.3f} {:>10.3f}"\
                    .format(m,*row[1:])
                s+=_s_

        h="\n{:-^"+str(l_s)+"}"
        h=h.format(" Timing stats ")
        if header:
            return h+h1+l+s+l
        else:
            return h1+s

    @classmethod
    def getStatsAsLists(cls):
        data=[]
        for m,v in cls.measures.items():
            data.append([m,len(v), min(v), numpy.percentile(v,0.25), mean(v), numpy.percentile(v,0.75),max(v), sum(v)])
        return data


    @classmethod
    def getStats(cls):
        stats={}
        h=["method", 'count', 'min', 'q25', 'avg', 'q75', 'max', 'sum']
        for row in cls.getStatsAsLists():
            stats[row[0]]={h[i]:row[i] for i in range(1, len(h))}
        return stats

    @classmethod
    def to_csv(cls, filename=None):
        import csv
        data = StringIO()
        csvw = csv.writer(data)

        csvw.writerow(["method",'count','min','q25','avg','q75','max','sum'])
        for row in cls.getStatsAsLists():
            csvw.writerow(row)
        if filename:
            with open(filename,'w') as f:
                f.write(data)
        data.seek(0)
        return data.read()


def timer(key=None, verbose=False, *func_or_func_args):
    def wrapped_f(f):

        @functools.wraps(f)
        def wrapped(*args, **kwargs):

            func_name = f.__name__
            #if key is None:
            #    key = func_name
            if key:
                with Timer(key=key, verbose=verbose) as t:
                    out = f(*args, **kwargs)
            else:
                with Timer(key=func_name, verbose=verbose) as t:
                    out = f(*args, **kwargs)
            return out
        return wrapped
    if (len(func_or_func_args) == 1
            and isinstance(func_or_func_args[0], collections.Callable)):
        return wrapped_f(func_or_func_args[0])
    else:
        return wrapped_f
