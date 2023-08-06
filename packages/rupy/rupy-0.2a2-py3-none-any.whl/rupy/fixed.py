import numbers

# functions which may return numeric types
num_ops = [
    "add", "sub", "mul", "floordiv", "truediv", "mod",
    "pow", "and" ,"or", "xor", "invert", "neg",
    "rshift", "lshift"
]

class FixedIntegerMeta(type):
    def __new__(mcs, name, bases, mdict, size=None):
        if size is None:

            def _op_wrap(func):
                def _wrapper(self, other):
                    res = func(self, other)
                    if isinstance(res, numbers.Number):
                        return self.__class__(res)
                    return res
                return _wrapper

            def _checked_op(func, name):
                def checked_op(self, other):
                    res = func(self, other)
                    if isinstance(res, numbers.Number):
                        if res > self.MAX:
                            raise OverflowError("Overflow performing %s on %s" % (name, self.__class__.__name__))
                        elif res < 0:
                            raise OverflowError("Underflow performing %s on %s" % (name, self.__class__.__name__))
                        res = self.__class__(res)
                    return res
                return checked_op

            for op in num_ops:
                method_name = "__%s__" % op
                method = getattr(int, method_name)
                mdict[method_name] = _op_wrap(method)
                mdict["checked_%s" % op] = _checked_op(method, op)
                rmethod_name = "__r%s__" % op
                rmethod = getattr(int, rmethod_name, None)
                if rmethod:
                    mdict[rmethod_name] = _op_wrap(rmethod)

        else:
            mdict['BITS'] = size
            mdict['MAX'] = mdict['MASK'] = 2 ** size - 1
        return type.__new__(mcs, name, bases, mdict,)

    def __init__(cls, *args, size=None, **kwargs):
        super().__init__(*args, **kwargs)


class FixedIntegerBase(int, metaclass=FixedIntegerMeta):
    def __new__(cls, n=0):
        return int.__new__(cls, n & cls.MASK)

    def rotate(self, right=0, left=0):
        if right and left:
            raise ValueError("Please make up your mind on which direction to rotate")
        rshift = (right - left) % self.BITS
        lshift = self.BITS - rshift
        return (self >> rshift) | (self << (lshift))



class Byte(FixedIntegerBase, size=8):
    pass

class Short(FixedIntegerBase, size=16):
    pass

Word = Short

class Dword(FixedIntegerBase, size=32):
    pass

Int = Dword

class Long(FixedIntegerBase, size=64):
    pass

Qword = Long

