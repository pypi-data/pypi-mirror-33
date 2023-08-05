import functools


class Pipe(object):
    __array_ufunc__ = None

    def __init__(self, func):
        self._aPpLy = func

    def __ror__(self, other):
        return self._aPpLy(other)

    def __contains__(self, item):
        return Pipe(lambda x: item in self._aPpLy(x))

    def __lt__(self, other):
        return Pipe(lambda x: self._aPpLy(x) < other)

    def __le__(self, other):
        return Pipe(lambda x: self._aPpLy(x) <= other)

    def __gt__(self, other):
        return Pipe(lambda x: self._aPpLy(x) > other)

    def __ge__(self, other):
        return Pipe(lambda x: self._aPpLy(x) >= other)

    def __eq__(self, other):
        return Pipe(lambda x: self._aPpLy(x) == other)

    def __ne__(self, other):
        return Pipe(lambda x: self._aPpLy(x) != other)

    def __or__(self, other):
        return Pipe(lambda x: self._aPpLy(x) | other)

    def __xor__(self, other):
        return Pipe(lambda x: self._aPpLy(x) ^ other)

    def __and__(self, other):
        return Pipe(lambda x: self._aPpLy(x) & other)

    def __rshift__(self, other):
        return Pipe(lambda x: self._aPpLy(x) >> other)

    def __lshift__(self, other):
        return Pipe(lambda x: self._aPpLy(x) << other)

    def __add__(self, other):
        return Pipe(lambda x: self._aPpLy(x) + other)

    def __sub__(self, other):
        return Pipe(lambda x: self._aPpLy(x) - other)

    def __mul__(self, other):
        return Pipe(lambda x: self._aPpLy(x) * other)

    def __matmul__(self, other):
        return Pipe(lambda x: self._aPpLy(x) @ other)

    def __truediv__(self, other):
        return Pipe(lambda x: self._aPpLy(x) / other)

    def __floordiv__(self, other):
        return Pipe(lambda x: self._aPpLy(x) // other)

    def __mod__(self, other):
        return Pipe(lambda x: self._aPpLy(x) % other)

    def __pos__(self):
        return Pipe(lambda x: +self._aPpLy(x))

    def __neg__(self):
        return Pipe(lambda x: -self._aPpLy(x))

    def __invert__(self):
        return Pipe(lambda x: ~self._aPpLy(x))

    def __pow__(self, power, modulo=None):
        return Pipe(lambda x: pow(self._aPpLy(x), power, modulo))

    def __await__(self):
        async def func(x):
            return await self._aPpLy(x)

        return Pipe(func)

    def __getitem__(self, item):
        return Pipe(lambda x: self._aPpLy(x)[item])

    def __call__(self, *args, **kwargs):
        return Pipe(lambda x: self._aPpLy(x)(*args, **kwargs))

    def __getattr__(self, attr):
        return Pipe(lambda x: getattr(self._aPpLy(x), attr))

    @staticmethod
    def patch_cls(cls):
        original = cls.__truediv__

        @functools.wraps(original)
        def wrapper(self, x):
            if isinstance(x, Pipe):
                return x.__rtruediv__(self)
            return original(self, x)

        cls.__truediv__ = wrapper

