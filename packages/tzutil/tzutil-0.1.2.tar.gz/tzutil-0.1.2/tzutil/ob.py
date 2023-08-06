#!/usr/bin/env python
# coding:utf-8


class Ob(object):

    def __init__(self, *args, **kwds):
        for i in args:
            self.__dict__.update(args)
        self.__dict__.update(kwds)

    def __getattr__(self, name):
        return self.__dict__.get(name, '')

    def __setattr__(self, name, value):
        if value is not None:
            self.__dict__[name] = value

    def __delattr__(self, name):
        if name in self.__dict__:
            del self.__dict__[name]

    def __repr__(self):
        return self.__dict__.__repr__()

    __getitem__ = __getattr__
    __delitem__ = __delattr__
    __setitem__ = __setattr__

    def __len__(self):
        return self.__dict__.__len__()

    def __iter__(self):
        for k, v in self.__dict__.items():
            yield k, v

    def __contains__(self, name):
        return self.__dict__.__contains__(name)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class StripOb(Ob):

    def __init__(self, *args, **kwds):
        super(StripJsOb, self).__init__(*args, **kwds)
        d = self.__dict__
        for k, v in d.items():
            if isinstance(v, str):
                if "\n" not in v:
                    _v = v.strip()
                    if _v != v:
                        d[k] = _v

if __name__ == '__main__':
    ob1 = Ob(a=1, b=2)

    # ob1.xx = None
    # print(ob1.__dict__)
    # del ob1.a
    # print(ob1.__dict__)
    # o = Ob(a='张沈鹏')
    # print(o)
    # for k, v in o:
    #     print(k, v)
    # print(dict)
    # print(dict(iter(o)))
