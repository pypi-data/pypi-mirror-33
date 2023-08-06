# Mdp Private Class(c). All rights reserved.
# Contact me for details. --- marcodp183@gmail.com ---
# This is a person Library for learning the arts of the Class and improving myself.
# Also there are some usefully mathematics function like Expression().linear(self, coeffxx, coeffyy, term), for
# resolving simple Linear Systems.
# I 'overload' some built_in types like Floating Points, Integer, and String. This don't create any problem with
# working with the prestabilied built_in types.
# This Library is under GNU License. For details read the GNU License clauses starting this Library from itself.
# GNU License imposes that the developer of the Library must be reported at the top of the it.
# Do not remove or modify this clauses during the distribution of this.
# For any details visit https://grigoprg.webnode.it

if __name__ == "__main__":
    _real_ = 1
    _notreal_ = 2
    __MainLibrary__ = "STX_LIB"


# START LIBRARY'S CLASSES FOR __SoftLib__ MODULE:

########################################## CLASS EXPRESSION ################################### Over:NONE | Under:List

import threading

class Expression():
    """
    Abstract class for expression resolving.
    """

    PI = 3.141592
    DEVELOPER = "Marco Della Putta"

    def __init__(self, name='Expression'):
        self.expression = name

    def exp_name(self):
        return str(self.expression)

    @classmethod
    def diagonal(cls, side1, side2):
        side1 = float(side1)
        side2 = float(side2)
        from math import sqrt
        from math import pow as pw
        return sqrt((pw(side1, 2)) + (pw(side2, 2)))

    @classmethod
    def c_area(cls, radius):
        radius = float(radius)
        from math import pow as pw
        return cls.PI * pw(radius, 2)

    @classmethod
    def radius(cls, area):
        area = float(area)
        from math import sqrt
        return sqrt((area / cls.PI))

    @classmethod
    def circ(cls, radius):
        radius = float(radius)
        return 2 * cls.PI * radius

    @classmethod
    def side(cls, area, side2):
        area = float(area)
        side2 = float(side2)
        return area / side2

    @classmethod
    def area(cls, side1, side2):
        side1 = float(side1)
        side2 = float(side2)
        return side1 * side2

    @classmethod
    def t_area(cls, high, base_max, base_min):
        high = float(high)
        base_max = float(base_max)
        base_min = float(base_min)
        return ((base_max + base_min) * high) / 2.0

    @classmethod
    def t_basemax(cls, high, area, base_min):
        high = float(high)
        area = float(area)
        base_min = float(base_min)
        return ((2.0 * area) / high) - base_min

    @classmethod
    def t_basemin(cls, high, area, base_max):
        high = float(high)
        area = float(area)
        base_max = float(base_max)
        return ((2.0 * area) / high) - base_max

    @classmethod
    def t_obside(cls, high, base_max, base_min):
        from math import sqrt
        from math import pow as pw
        high = float(high)
        base_max = float(base_max)
        base_min = float(base_min)
        return sqrt(pw(high, 2) + pw((base_max - base_min), 2))

    @classmethod
    def t_diagonalmax(cls, high, base_max):
        base_max = float(base_max)
        high = float(high)
        from math import sqrt
        from math import pow as pw
        return sqrt(pw(high, 2) + pw(base_max, 2))

    @classmethod
    def t_diagonalmin(cls, high, base_min):
        base_min = float(base_min)
        high = float(high)
        from math import sqrt
        from math import pow as pw
        return sqrt(pw(high, 2) + pw(base_min, 2))

    @classmethod
    def t_high(cls, area, base_max, base_min):
        area = float(area)
        base_max = float(base_max)
        base_min = float(base_min)
        return (2.0 * area) / (base_min + base_max)

    @classmethod
    def class_name(cls):
        return cls.__name__

    @classmethod
    def add(cls, num1, num2):
        if isinstance(num1, Float) or isinstance(num1, Int):
            num1 = num1.num
        if isinstance(num2, Float) or isinstance(num2, Int):
            num2 = num2.num
        from math import fsum
        num1 = float(num1)
        num2 = float(num2)
        num3 = [num1, num2]
        return fsum(num3)

    @classmethod
    def sub(cls, num1, num2):
        if isinstance(num1, Float) or isinstance(num1, Int):
            num1 = num1.num
        if isinstance(num2, Float) or isinstance(num2, Int):
            num2 = num2.num
        num1 = float(num1)
        num2 = float(num2)
        return num1 - num2

    @classmethod
    def mul(cls, num1, num2):
        if isinstance(num1, Float) or isinstance(num1, Int):
            num1 = num1.num
        if isinstance(num2, Float) or isinstance(num2, Int):
            num2 = num2.num
        num1 = float(num1)
        num2 = float(num2)
        return num1 * num2

    @classmethod
    def div(cls, num1, num2):
        if isinstance(num1, Float) or isinstance(num1, Int):
            num1 = num1.num
        if isinstance(num2, Float) or isinstance(num2, Int):
            num2 = num2.num
        num1 = float(num1)
        num2 = float(num2)
        return num1 / num2

    @classmethod
    def floor(cls, num1, num2):
        if isinstance(num1, Float) or isinstance(num1, Int):
            num1 = num1.num
        if isinstance(num2, Float) or isinstance(num2, Int):
            num2 = num2.num
        num1 = float(num1)
        num2 = float(num2)
        return num1 // num2

    @classmethod
    def mod(cls, num1, num2):
        if isinstance(num1, Float) or isinstance(num1, Int):
            num1 = num1.num
        if isinstance(num2, Float) or isinstance(num2, Int):
            num2 = num2.num
        from math import fmod
        num1 = float(num1)
        num2 = float(num2)
        return fmod(num1, num2)

    @classmethod
    def pow(cls, num1, num2):
        if isinstance(num1, Float) or isinstance(num1, Int):
            num1 = num1.num
        if isinstance(num2, Float) or isinstance(num2, Int):
            num2 = num2.num
        from math import pow as pw
        num1 = float(num1)
        num2 = float(num2)
        return pw(num1, num2)

    @classmethod
    def sqrt(cls, num1):
        if isinstance(num1, Float) or isinstance(num1, Int):
            num1 = num1.num
        if isinstance(num1, Float) or isinstance(num1, Int):
            num1 = num1.num
        num1 = float(num1)
        from math import sqrt
        return sqrt(num1)

    @classmethod
    def linear(cls, coeffxx, coeffyy, termm):
        if isinstance(coeffxx, Float) or isinstance(coeffxx, Int):
            coeffxx = coeffxx.num
        if isinstance(coeffyy, Float) or isinstance(coeffyy, Int):
            coeffyy = coeffyy.num
        if isinstance(termm, Float) or isinstance(termm, Int):
            termm = termm.num

        D = (float(coeffxx[0] * coeffyy[1]) - float(coeffyy[0] * coeffxx[1]))
        DX = (float(termm[0] * coeffyy[1]) - float(coeffyy[0] * termm[1]))
        DY = (float(coeffxx[0] * termm[1]) - float(termm[0] * coeffxx[1]))
        X = DX / D
        Y = DY / D
        return round(X, 1), round(Y, 1)

    @classmethod
    def delta(cls, coeffxx, coeffx, term):
        if isinstance(coeffxx, Float) or isinstance(coeffxx, Int):
            coeffxx = coeffxx.num
        if isinstance(coeffx, Float) or isinstance(coeffx, Int):
            coeffx = coeffx.num
        if isinstance(term, Float) or isinstance(term, Int):
            term = term.num

        from math import pow as pw
        DELTA = float(pw(coeffx, 2) - (4 * term * coeffxx))
        return DELTA

    @classmethod
    def expression2(cls, coeffxx, coeffx, term):
        if isinstance(coeffxx, Float) or isinstance(coeffxx, Int):
            coeffxx = coeffxx.num
        if isinstance(coeffx, Float) or isinstance(coeffx, Int):
            coeffx = coeffx.num
        if isinstance(term, Float) or isinstance(term, Int):
            term = term.num
        from math import sqrt
        try:
            DELTA = cls.delta(coeffxx, coeffx, term)
            X1 = (-coeffx - sqrt(DELTA)) / (2 * coeffxx)
            X2 = (-coeffx + sqrt(DELTA)) / (2 * coeffxx)
            return round(X1, 1), round(X2, 1)
        except ValueError:
            return False

########################################### LIST CLASS ################################## Over:Expression | Under:Float

class List:
    """
    Class for the overload of the built-in type 'list'.
    """

    DEVELOPER = "Marco Della Putta"

    def __init__(self, _list=False):
        if not _list:
            self.list = []
        else:
            try:
                if isinstance(_list, List):
                    self.list = _list.list
                elif isinstance(_list, list) or isinstance(_list, frozenset) or isinstance(_list, set) or isinstance(_list, tuple):
                    _list = list(_list)
                    self.list = _list
                    self.list = list(self.list)
                else:
                    self.list = []
                    self.list.append(_list)
            except TypeError or AttributeError or ValueError:
                self.list = []

    @classmethod
    def class_name(cls):
        return cls.__name__

    def len(self):
        return len(self.list)

    def iter(self):
        ctr = 0
        while ctr < self.len():
            yield self.list[ctr]
            ctr += 1

    def sort(self):
        self.list.sort()
        return List(self.list)

    def __str__(self):
        return str(self.list)

    def __repr__(self):
        return str(self.list)

    def __getitem__(self, item):
        return self.list[item]

    def __setitem__(self, key, value):
        self.list[key] = value
        return List(self.list)

    def __add__(self, other):
        if isinstance(other, list) or isinstance(other, set) or isinstance(other, frozenset) or isinstance(other,tuple):
            other = list(other)
            x = self.list + list(other)
            return List(x)
        elif isinstance(other, List):
            x = self.list + other.list
            return List(x)
        else:
            x = self.list
            x.append(other)
            return List(x)

    def __mul__(self, other):
        if isinstance(other, list) or isinstance(other, set) or isinstance(other, frozenset) or isinstance(other,tuple):
            from itertools import product
            other = list(other)
            x = product(self.list, list(other))
            x = list(x)
            return List(x)
        elif isinstance(other, List):
            from itertools import product
            x = product(self.list, other.list)
            x = list(x)
            return List(x)
        else:
            try:
                other = int(other)
                x = self.list * other
                return List(x)
            except:
                raise TypeError

    def __sub__(self, other):
        if isinstance(other, list) or isinstance(other, set) or isinstance(other, frozenset) or isinstance(other,tuple):
            other = list(other)
            res = []
            for x in self.list:
                if x not in other:
                    res.append(x)
            return List(res)
        elif isinstance(other, List):
            res = []
            for x in self.list:
                if x not in other.list:
                    res.append(x)
            return List(res)
        else:
            try:
                x = self.list
                if other in x:
                    x.remove(other)
                return List(x)
            except TypeError or ValueError or AttributeError or IndexError:
                raise TypeError

    def __contains__(self, item):
        if isinstance(item, List):
            if item.list in self.list:
                return True
            else:
                return False
        else:
            try:
                if item in self.list:
                    return True
                else:
                    return False
            except ValueError or AttributeError or TypeError:
                raise TypeError

    def __neg__(self):
        try:
            res = self.list
            res2 = []
            for x in res:
                if x > 0:
                    x *= -1
                    res2.append(x)

            return List(res2)
        except:
            raise TypeError

    def __bool__(self):
        if self.list:
            return True
        else:
            return False

    def __reversed__(self):
        x = self.list
        x = x[::-1]
        return List(x)

    def __abs__(self):
        try:
            res = self.list
            res2 = []
            for x in res:
                x = abs(x)
                res2.append(x)

            return List(res2)
        except ValueError or TypeError or AttributeError or IndexError:
            raise TypeError

    def __int__(self):
        try:
            res = self.list
            res2 = []
            for x in res:
                x = int(x)
                res2.append(x)

            return List(res2)
        except ValueError or TypeError or AttributeError:
            raise TypeError

    def __float__(self):
        try:
            res = self.list
            res2 = []
            for x in res:
                x = float(x)
                res2.append(x)

            return List(res2)
        except ValueError or TypeError or AttributeError:
            raise TypeError

    def __delitem__(self, key):
        try:
            self.list.pop(key)
        except TypeError or ValueError or AttributeError:
            raise TypeError
        except IndexError:
            raise IndexError

    def __copy__(self):
        return List(self.list.copy())

    def __gt__(self, other):
        if isinstance(other, list) or isinstance(other, set) or isinstance(other, frozenset) or isinstance(other,tuple):
            other = list(other)
            if len(self.list) > len(other):
                return True
            else:
                return False
        elif isinstance(other, List):
            if len(self.list) > len(other.list):
                return True
            else:
                return False
        else:
            try:
                if len(self.list) > int(other):
                    return True
                else:
                    return False
            except ValueError or TypeError or AttributeError:
                raise TypeError

    def __ge__(self, other):
        if isinstance(other, list) or isinstance(other, set) or isinstance(other, frozenset) or isinstance(other,tuple):
            other = list(other)
            if len(self.list) >= len(other):
                return True
            else:
                return False
        elif isinstance(other, List):
            if len(self.list) >= len(other.list):
                return True
            else:
                return False
        else:
            try:
                if len(self.list) >= int(other):
                    return True
                else:
                    return False
            except ValueError or TypeError or AttributeError:
                raise TypeError

    def __lt__(self, other):
        if isinstance(other, list) or isinstance(other, set) or isinstance(other, frozenset) or isinstance(other,tuple):
            other = list(other)
            if len(self.list) < len(other):
                return True
            else:
                return False
        elif isinstance(other, List):
            if len(self.list) < len(other.list):
                return True
            else:
                return False
        else:
            try:
                if len(self.list) < int(other):
                    return True
                else:
                    return False
            except ValueError or TypeError or AttributeError:
                raise TypeError

    def __le__(self, other):
        if isinstance(other, list) or isinstance(other, set) or isinstance(other, frozenset) or isinstance(other,tuple):
            other = list(other)
            if len(self.list) <= len(other):
                return True
            else:
                return False
        elif isinstance(other, List):
            if len(self.list) <= len(other.list):
                return True
            else:
                return False
        else:
            try:
                if len(self.list) <= int(other):
                    return True
                else:
                    return False
            except ValueError or TypeError or AttributeError:
                raise TypeError

    def __eq__(self, other):
        if isinstance(other, list) or isinstance(other, set) or isinstance(other, frozenset) or isinstance(other,tuple):
            other = list(other)
            if self.list == other:
                return True
            else:
                return False
        elif isinstance(other, List):
            if self.list == other.list:
                return True
            else:
                return False

        elif isinstance(other, str):
            other = list(other)
            if self.list == other:
                return True
            else:
                return False
        else:
            raise TypeError

    def __ne__(self, other):
        if isinstance(other, list) or isinstance(other, set) or isinstance(other, frozenset) or isinstance(other,tuple):
            other = list(other)
            if self.list != other:
                return True
            else:
                return False
        elif isinstance(other, List):
            if self.list != other.list:
                return True
            else:
                return False

        elif isinstance(other, str):
            other = list(other)
            if self.list != other:
                return True
            else:
                return False
        else:
            raise TypeError

    def __len__(self):
        return len(self.list)

    def __call__(self, funct):
        try:
            x = funct(self.list)
            return List(x)
        except:
            raise TypeError

    def __pow__(self, power):
        res = List(self.list)
        for x in range(power):
            res = res * res
        return List(res)

    def __mod__(self, other):
        res = []
        if isinstance(other, list) or isinstance(other, frozenset) or isinstance(other, set) or isinstance(other,tuple) or isinstance(other, str):
            other = list(other)
            for x in self.list:
                if x not in other:
                    res.append(x)
            return List(res)
        elif isinstance(other, List):
            for x in self.list:
                if x not in other.list:
                    res.append(x)
            return List(res)
        else:
            try:
                res = self.list
                if other in res:
                    res.remove(other)
                return List(res)
            except ValueError or IndexError or ValueError or AttributeError:
                raise TypeError

    def __imul__(self, other):
        if isinstance(other, list) or isinstance(other, set) or isinstance(other, frozenset) or isinstance(other,tuple):
            from itertools import product
            other = list(other)
            self.list = list(product(self.list, other))
            return List(self.list)
        elif isinstance(other, List):
            from itertools import product
            self.list = list(product(self.list, other.list))
            self.list = list(self.list)  # For more security
            return List(self.list)
        else:
            try:
                other = int(other)
                self.list = self.list * other
                return List(self.list)
            except:
                raise TypeError

    def __isub__(self, other):
        if isinstance(other, list) or isinstance(other, set) or isinstance(other, frozenset) or isinstance(other,tuple):
            other = list(other)
            res = []
            for x in self.list:
                if x not in other:
                    res.append(x)
            self.list = res.copy()
            return List(self.list)
        elif isinstance(other, List):
            res = []
            for x in self.list:
                if x not in other.list:
                    res.append(x)
            self.list = res.copy()
            return List(self.list)
        else:
            try:
                if other in self.list:
                    self.list.remove(other)
                return List(self.list)
            except TypeError or ValueError or AttributeError or IndexError:
                raise TypeError

    def __iadd__(self, other):
        if isinstance(other, list) or isinstance(other, set) or isinstance(other, frozenset) or isinstance(other,tuple):
            other = list(other)
            self.list = self.list + list(other)
            return List(self.list)
        elif isinstance(other, List):
            self.list = self.list + other.list
            return List(self.list)
        else:
            self.list.append(other)
            return List(self.list)

    def append(self, other):
        self.list.append(other)
        return List(self.list)

    def pop(self, index):
        try:
            index = int(index)
            self.list.pop(index)
            return List(self.list)
        except ValueError and TypeError and IndexError and AttributeError:
            raise TypeError

    def remove(self, value):
        if value in self.list:
            self.list.remove(value)
            return List(self.list)
        else:
            return None

    def replace(self, old_value, new_value):
        cpy = self.list
        for x in self.list:
            if x == old_value:
                cpy.append(new_value)
            else:
                cpy.append(x)
        self.list = cpy.copy()
        return List(self.list)

    def map(self, funct):
        try:
            self.list = list(funct(self.list))
            return List(self.list)
        except:
            raise TypeError

    def set(self, other):
        if isinstance(other, list) or isinstance(other, set) or isinstance(other, frozenset) or isinstance(other,tuple) or isinstance(other, str):
            self.list = list(other)
        elif isinstance(other, List):
            self.list = other.list
        else:
            self.list = []
            self.list.append(other)

    def get(self):
        return list(self.list)

    def encrypt(self, key):
        cpy = []
        for x in self.list:
            x ^= key
            cpy.append(x)

        self.list = cpy.copy()
        return List(self.list)

    def decrypt(self, key):
        cpy = []
        for x in self.list:
            x ^= key
            cpy.append(x)

        self.list = cpy.copy()
        return List(self.list)

    def string(self):
        return String(self.list)

    def sum(self):
        return sum(self.list)

    def product(self):
        try:
            res = 0
            for x in self.list:
                res *= x
            return res
        except ValueError or TypeError or AttributeError or IndexError:
            raise TypeError

    def int(self):
        try:
            x = String(self.list)
            x = x.int()
            return x
        except:
            raise TypeError

    def float(self):
        try:
            x = String(self.list)
            x = x.float()
            return x
        except:
            raise TypeError

################################################ FLOAT CLASS #################################### Over:List | Under:Int

class Float:
    """
    Overload of Float class.
    """

    DEVELOPER = "Marco Della Putta"

    def __init__(self, num=0.0):
        try:
            self.num = float(num)
        except:
            try:
                self.num = float(len(num))
            except:
                raise TypeError

    def __float__(self):
        try:
            x = float(self.num)
            return x
        except:
            raise TypeError

    def __int__(self):
        try:
            x = int(self.num)
            return x
        except:
            raise TypeError

    def __call__(self, funct):
        try:
            x = funct(self.num)
            return Float(x)
        except:
            raise TypeError

    def __ne__(self, other):
        if isinstance(other, Float):
            if self.num != other.num:
                return True
            else:
                return False
        elif isinstance(other, int) or isinstance(other, float):
            other = float(other)
            if self.num != other:
                return True
            else:
                return False
        else:
            try:
                xy = float(len(other))
                if self.num != xy:
                    return True
                else:
                    return False
            except:
                raise TypeError

    def __eq__(self, other):
        if isinstance(other, Float):
            if self.num == other.num:
                return True
            else:
                return False
        elif isinstance(other, int) or isinstance(other, float):
            other = float(other)
            if self.num == other:
                return True
            else:
                return False
        else:
            try:
                xy = float(len(other))
                if self.num == xy:
                    return True
                else:
                    return False
            except:
                raise TypeError

    def __lt__(self, other):
        if isinstance(other, Float):
            if self.num < other.num:
                return True
            else:
                return False
        elif isinstance(other, int) or isinstance(other, float):
            other = float(other)
            if self.num < other:
                return True
            else:
                return False
        else:
            try:
                xy = float(len(other))
                if self.num < xy:
                    return True
                else:
                    return False
            except:
                raise TypeError

    def __le__(self, other):
        if isinstance(other, Float):
            if self.num <= other.num:
                return True
            else:
                return False
        elif isinstance(other, int) or isinstance(other, float):
            other = float(other)
            if self.num <= other:
                return True
            else:
                return False
        else:
            try:
                xy = float(len(other))
                if self.num <= xy:
                    return True
                else:
                    return False
            except:
                raise TypeError

    def __gt__(self, other):
        if isinstance(other, Float):
            if self.num > other.num:
                return True
            else:
                return False
        elif isinstance(other, int) or isinstance(other, float):
            other = float(other)
            if self.num > other:
                return True
            else:
                return False
        else:
            try:
                xy = float(len(other))
                if self.num > xy:
                    return True
                else:
                    return False
            except:
                raise TypeError

    def __ge__(self, other):
        if isinstance(other, Float):
            if self.num >= other.num:
                return True
            else:
                return False
        elif isinstance(other, int) or isinstance(other, float):
            other = float(other)
            if self.num >= other:
                return True
            else:
                return False
        else:
            try:
                xy = float(len(other))
                if self.num >= xy:
                    return True
                else:
                    return False
            except:
                raise TypeError

    def __add__(self, other):
        if isinstance(other, Float):
            x = self.num + other.num
            return Float(x)
        else:
            try:
                other = float(other)
                x = self.num + other
                return Float(x)
            except:
                try:
                    x = self.num + float(len(other))
                    return Float(x)
                except:
                    raise TypeError

    def __sub__(self, other):
        if isinstance(other, Float):
            x = self.num - other.num
            return Float(x)
        else:
            try:
                other = float(other)
                x = self.num - other
                return Float(x)
            except:
                try:
                    x = self.num - float(len(other))
                    return Float(x)
                except:
                    raise TypeError

    def __mul__(self, other):
        if isinstance(other, Float):
            x = self.num * other.num
            return Float(x)
        else:
            try:
                other = float(other)
                x = self.num * other
                return Float(x)
            except:
                try:
                    x = self.num * float(len(other))
                    return Float(x)
                except:
                    raise TypeError

    def __truediv__(self, other):
        if isinstance(other, Float):
            x = float(self.num / other.num)
            return Float(x)
        else:
            try:
                other = float(other)
                x = float(self.num / other)
                return Float(x)
            except:
                try:
                    x = float(self.num / float(len(other)))
                    return Float(x)
                except:
                    raise TypeError

    def __floordiv__(self, other):
        if isinstance(other, Float):
            x = float(self.num // other.num)
            return Float(x)
        else:
            try:
                other = float(other)
                x = float(self.num // other)
                return Float(x)
            except:
                try:
                    x = float(self.num // float(len(other)))
                    return Float(x)
                except:
                    raise TypeError

    def __repr__(self):
        return str(self.num)

    def __str__(self):
        return str(self.num)

    def __bool__(self):
        if self.num == 0.0:
            return False
        else:
            return True

    def __reversed__(self):
        return Float(self.num * -1.0)

    def __abs__(self):
        import math
        return Float(math.fabs(self.num))

    def __del__(self):
        self.num = None
        return None

    def __mod__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            other = float(other)
            x = self.num % other
            return Float(x)
        elif isinstance(other, Float):
            other.num = float(other.num)
            x = self.num % other.num
            return Float(x)
        else:
            try:
                xy = float(len(other))
                x = self.num % xy
                return Float(x)
            except:
                raise TypeError

    def __neg__(self):
        return Float(self.num * -1.0)

    def __pos__(self):
        return Float(self.num * 1.0)

    def __pow__(self, power):
        x = self.num ** power
        return Float(x)

    def __iadd__(self, other):
        if isinstance(other, Float):
            self.num = self.num + other.num
            return Float(self.num)
        else:
            try:
                other = float(other)
                self.num = self.num + other
                return Float(self.num)
            except:
                try:
                    self.num = self.num + float(len(other))
                    return Float(self.num)
                except:
                    raise TypeError

    def __isub__(self, other):
        if isinstance(other, Float):
            self.num = self.num - other.num
            return Float(self.num)
        else:
            try:
                other = float(other)
                self.num = self.num - other
                return Float(self.num)
            except:
                try:
                    self.num = self.num - float(len(other))
                    return Float(self.num)
                except:
                    raise TypeError

    def __imul__(self, other):
        if isinstance(other, Float):
            self.num = self.num * other.num
            return Float(self.num)
        else:
            try:
                other = float(other)
                self.num = self.num * other
                return Float(self.num)
            except:
                try:
                    self.num = self.num * float(len(other))
                    return Float(self.num)
                except:
                    raise TypeError

    def __idiv__(self, other):
        if isinstance(other, Float):
            self.num = self.num / other.num
            return Float(self.num)
        else:
            try:
                other = float(other)
                self.num = self.num / other
                return Float(self.num)
            except:
                try:
                    self.num = self.num / float(len(other))
                    return Float(self.num)
                except:
                    raise TypeError

    def __imod__(self, other):
        if isinstance(other, Float):
            self.num = self.num % other.num
            return Float(self.num)
        else:
            try:
                other = float(other)
                self.num = self.num % other
                return Float(self.num)
            except:
                try:
                    self.num = self.num % float(len(other))
                    return Float(self.num)
                except:
                    raise TypeError

    def __ifloordiv__(self, other):
        if isinstance(other, Float):
            self.num = self.num // other.num
            return Int(self.num)
        else:
            try:
                other = float(other)
                self.num = self.num // other
                return Float(self.num)
            except:
                try:
                    self.num = self.num // float(len(other))
                    return Float(self.num)
                except:
                    raise TypeError

    def __ipow__(self, other):
        other = float(other)
        self.num = self.num ** other
        return Float(self.num)

    @classmethod
    def class_name(cls):
        return cls.__name__

    def get(self):
        return Float(self.num)

    def get_int(self):
        return int(self.num)

    def get_float(self):
        return float(self.num)

    def get_string(self):
        return str(self.num)

    def rand(self, start_value=0, stop_value=100):
        import random
        if start_value == 0 and stop_value == 100:
            self.num = random.uniform(0.0, 100.0)
            return Float(self.num)
        elif start_value != 0 and stop_value == 100:
            self.num = random.uniform(0, start_value)
            return Float(self.num)
        else:
            self.num = random.uniform(start_value, stop_value)
            return Float(self.num)

    def int(self):
        return Int(self.num)

    def string(self):
        return String(self.num)

    def list(self):
        return List(self.num)

########################################## INT CLASS ######################################## Over:Float | Under:String

class Int:
    """
    Overload of Int class.
    """

    DEVELOPER = "Marco Della Putta"

    def __init__(self, num=0):
        try:
            self.num = int(num)
        except:
            try:
                self.num = len(num)
            except:
                raise TypeError

    def __float__(self):
        try:
            x = float(self.num)
            return x
        except:
            raise TypeError

    def __int__(self):
        try:
            x = int(self.num)
            return x
        except:
            raise TypeError

    def iter(self):
        ctr = 0
        while ctr < self.num:
            yield ctr
            ctr += 1

    def __call__(self, funct):
        try:
            x = funct(self.num)
            return Int(x)
        except:
            raise TypeError

    def __ne__(self, other):
        if isinstance(other, Int):
            if self.num != other.num:
                return True
            else:
                return False
        elif isinstance(other, int) or isinstance(other, float):
            if self.num != other:
                return True
            else:
                return False
        else:
            try:
                xy = len(other)
                if self.num != xy:
                    return True
                else:
                    return False
            except:
                raise TypeError

    def __eq__(self, other):
        if isinstance(other, Int):
            if self.num == other.num:
                return True
            else:
                return False
        elif isinstance(other, int) or isinstance(other, float):
            if self.num == other:
                return True
            else:
                return False
        else:
            try:
                xy = len(other)
                if self.num == xy:
                    return True
                else:
                    return False
            except:
                raise TypeError

    def __lt__(self, other):
        if isinstance(other, Int):
            if self.num < other.num:
                return True
            else:
                return False
        elif isinstance(other, int) or isinstance(other, float):
            if self.num < other:
                return True
            else:
                return False
        else:
            try:
                xy = len(other)
                if self.num < xy:
                    return True
                else:
                    return False
            except:
                raise TypeError

    def __le__(self, other):
        if isinstance(other, Int):
            if self.num <= other.num:
                return True
            else:
                return False
        elif isinstance(other, int) or isinstance(other, float):
            if self.num <= other:
                return True
            else:
                return False
        else:
            try:
                xy = len(other)
                if self.num <= xy:
                    return True
                else:
                    return False
            except:
                raise TypeError

    def __gt__(self, other):
        if isinstance(other, Int):
            if self.num > other.num:
                return True
            else:
                return False
        elif isinstance(other, int) or isinstance(other, float):
            if self.num > other:
                return True
            else:
                return False
        else:
            try:
                xy = len(other)
                if self.num > xy:
                    return True
                else:
                    return False
            except:
                raise TypeError

    def __ge__(self, other):
        if isinstance(other, Int):
            if self.num >= other.num:
                return True
            else:
                return False
        elif isinstance(other, int) or isinstance(other, float):
            if self.num >= other:
                return True
            else:
                return False
        else:
            try:
                xy = len(other)
                if self.num >= xy:
                    return True
                else:
                    return False
            except:
                raise TypeError

    def __add__(self, other):
        if isinstance(other, Int):
            x = self.num + other.num
            return Int(x)
        else:
            try:
                x = self.num + other
                return Int(x)
            except:
                try:
                    x = self.num + len(other)
                    return Int(x)
                except:
                    raise TypeError

    def __sub__(self, other):
        if isinstance(other, Int):
            x = self.num - other.num
            return Int(x)
        else:
            try:
                x = self.num - other
                return Int(x)
            except:
                try:
                    x = self.num - len(other)
                    return Int(x)
                except:
                    raise TypeError

    def __mul__(self, other):
        if isinstance(other, Int):
            x = self.num * other.num
            return Int(x)
        else:
            try:
                x = self.num * other
                return Int(x)
            except:
                try:
                    x = self.num * len(other)
                    return Int(x)
                except:
                    raise TypeError

    def __truediv__(self, other):
        if isinstance(other, Int):
            x = int(self.num / other.num)
            return Int(x)
        else:
            try:
                x = int(self.num / other)
                return Int(x)
            except:
                try:
                    x = int(self.num / len(other))
                    return Int(x)
                except:
                    raise TypeError

    def __floordiv__(self, other):
        if isinstance(other, Int):
            x = int(self.num // other.num)
            return Int(x)
        else:
            try:
                x = int(self.num // other)
                return Int(x)
            except:
                try:
                    x = int(self.num // len(other))
                    return Int(x)
                except:
                    raise TypeError

    def __repr__(self):
        return str(self.num)

    def __str__(self):
        return str(self.num)

    def __bool__(self):
        if self.num == 0:
            return False
        else:
            return True

    def __reversed__(self):
        return Int(self.num * -1)

    def __abs__(self):
        return Int(abs(self.num))

    def __del__(self):
        self.num = None
        return None

    def __mod__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            other = int(other)
            x = self.num % other
            return Int(x)
        elif isinstance(other, Int):
            other.num = int(other.num)
            x = self.num % other.num
            return Int(x)
        else:
            try:
                xy = len(other)
                x = self.num % xy
                return Int(x)
            except:
                raise TypeError

    def __neg__(self):
        return Int(self.num * -1)

    def __pos__(self):
        return Int(self.num * 1)

    def __pow__(self, power):
        x = self.num ** power
        return Int(x)

    def __iadd__(self, other):
        if isinstance(other, Int):
            self.num = self.num + other.num
            return Int(self.num)
        else:
            try:
                self.num = self.num + other
                return Int(self.num)
            except:
                try:
                    self.num = self.num + len(other)
                    return Int(self.num)
                except:
                    raise TypeError

    def __isub__(self, other):
        if isinstance(other, Int):
            self.num = self.num - other.num
            return Int(self.num)
        else:
            try:
                self.num = self.num - other
                return Int(self.num)
            except:
                try:
                    self.num = self.num - len(other)
                    return Int(self.num)
                except:
                    raise TypeError

    def __imul__(self, other):
        if isinstance(other, Int):
            self.num = self.num * other.num
            return Int(self.num)
        else:
            try:
                self.num = self.num * other
                return Int(self.num)
            except:
                try:
                    self.num = self.num * len(other)
                    return Int(self.num)
                except:
                    raise TypeError

    def __idiv__(self, other):
        if isinstance(other, Int):
            self.num = self.num / other.num
            return Int(self.num)
        else:
            try:
                self.num = self.num / other
                return Int(self.num)
            except:
                try:
                    self.num = self.num / len(other)
                    return Int(self.num)
                except:
                    raise TypeError

    def __imod__(self, other):
        if isinstance(other, Int):
            self.num = self.num % other.num
            return Int(self.num)
        else:
            try:
                self.num = self.num % other
                return Int(self.num)
            except:
                try:
                    self.num = self.num % len(other)
                    return Int(self.num)
                except:
                    raise TypeError

    def __ifloordiv__(self, other):
        if isinstance(other, Int):
            self.num = self.num // other.num
            return Int(self.num)
        else:
            try:
                self.num = self.num // other
                return Int(self.num)
            except:
                try:
                    self.num = self.num // len(other)
                    return Int(self.num)
                except:
                    raise TypeError

    def __ipow__(self, other):
        self.num = self.num ** other
        return Int(self.num)

    @classmethod
    def class_name(cls):
        return cls.__name__

    def get(self):
        return Int(self.num)

    def get_int(self):
        return int(self.num)

    def get_float(self):
        return float(self.num)

    def get_string(self):
        return str(self.num)

    def rand(self, start_value=0, stop_value=100):
        import random
        if start_value == 0 and stop_value == 100:
            self.num = random.randrange(start_value, stop_value)
            return Int(self.num)
        elif start_value != 0 and stop_value == 100:
            self.num = random.randrange(0, start_value)
            return Int(self.num)
        else:
            self.num = random.randrange(start_value, stop_value)
            return Int(self.num)

    def float(self):
        return Float(self.num)

    def string(self):
        return String(self.num)

    def list(self):
        return List(self.num)

########################################### STRING CLASS ####################################### Over:Int | Under:Point


class String:
    """
    Usefully set of functions for better working.
    Class developed by Mdp Inc.
    """
    DEVELOPER = "Marco Della Putta"

    def __init__(self, name=""):
        """
        __init__ method for Mdp String class.
        param : self, name[optional]
        return : None
        """
        try:
            name = str(name)
            self.string = name
            self.string = str(self.string)
        except AttributeError or ValueError or TypeError:
            raise TypeError

    @classmethod
    def class_name(cls):
        return cls.__name__

    def __str__(self):
        """
        __str__ method for printing string.
        param : self
        return : self.string (the string object)
        """
        return self.string

    def __add__(self, other):
        """
        __add__ method for adding string.
        param : self, other
        return : self.string (the string object)
        """
        other = str(other)
        xx = self.string + other
        return String(xx)

    def append(self, other):
        other = str(other)
        self.string = self.string + other
        return String(self.string)

    def len(self):
        return len(self.string)

    def iter(self):
        ctr = 0
        while ctr < self.len():
            yield self.string[ctr]
            ctr += 1

    def __mul__(self, other):
        """
        __mul__ method for multiplication of string.
        param : self, other
        return : self.string (the string object)
        """
        try:
            other = int(other)
            xx = self.string * other
            return String(xx)
        except:
            raise TypeError

    def __repr__(self):
        return self.string

    def __bool__(self):
        if not self.string:
            return False
        else:
            return True

    def __len__(self):
        return len(self.string)

    def __eq__(self, other):
        other = str(other)
        if self.string == other:
            return True
        else:
            return False

    def get(self):
        """
        Getter method for class Mdp String.
        param : self
        return : self.string (the string object)
        """
        return self.string

    def set(self, x):
        """
        Setter method for class Mdp String.
        param : self, string
        return : self.string (the string object)
        """
        x = str(x)
        self.string = x
        return String(self.string)

    def reset(self):
        """
        Method for reset a string.
        param : self
        return : self.string (the string object)
        """
        self.string = ""
        return String(self.string)

    def __sub__(self, other):
        """
        __sub__ method for string subtraction.
        param : self, other
        return : self.string (the string object)
        """
        other = str(other)
        if other in self.string:
            xx = self.string.replace(other, "")
            return String(xx)
        else:
            print(">>> ERROR. Parameter not in string <<<")
            return -1

    def __reversed__(self):
        x = self.string
        x = x[::-1]
        return String(self.string)

    def __ne__(self, other):
        other = str(other)
        if self.string == other:
            return False
        else:
            return True

    def __gt__(self, other):
        other = str(other)
        if len(self.string) > len(other):
            return True
        else:
            return False

    def __lt__(self, other):
        other = str(other)
        if len(self.string) < len(other):
            return True
        else:
            return False

    def __le__(self, other):
        other = str(other)
        if len(self.string) <= len(other):
            return True
        else:
            return False

    def __ge__(self, other):
        other = str(other)
        if len(self.string) < len(other):
            return True
        else:
            return False

    def __getitem__(self, item):
        try:
            item = int(item)
            return String(self.string[item])
        except:
            raise TypeError

    def __contains__(self, item):
        item = str(item)
        if item in self.string:
            return True
        else:
            return False

    def remove(self, x):
        """
        Advanced Dynamic Removing Method (ADRM) for Mdp String class.
        param : self, x --- x can be all type
        return : self.string (the string object)
        """
        if isinstance(x, list):
            ctr = 0
            for elem in x:
                self.string = self.string[:elem - ctr] + self.string[(elem + 1 - ctr):]
                ctr += 1
            return String(self.string)
        elif isinstance(x, int):
            self.string = self.string[:x] + self.string[(x + 1):]
            return String(self.string)
        elif isinstance(x, float):
            x = int(x)
            self.string = self.string[:x] + self.string[(x + 1):]
            return String(self.string)
        elif isinstance(x, str):
            self.string = self.string.replace(x, "")
            return String(self.string)
        else:
            print(">>> ERROR. Invalid argument type.")
            return -1

    def replace(self, old, new, max=1000):
        if max == 1000:
            try:
                self.string.replace(old, new)
                return String(self.string)
            except:
                raise TypeError
        else:
            try:
                self.string.replace(old, new, max)
                return String(self.string)
            except:
                raise TypeError

    def int(self):
        try:
            x = self.string
            try:
                x = int(x)
                return Int(x)
            except:
                return Int(self.string)
        except:
            raise TypeError

    def float(self):
        try:
            x = self.string
            try:
                x = int(x)
                return Int(x)
            except:
                return Float(self.string)
        except:
            raise TypeError

    def list(self):
        try:
            return List(self.string)
        except:
            raise TypeError

############################################## POINT CLASS ################################ Over:String | Under:Point3D

class Point:
    """
    Base class for creation of points.
    """

    DEVELOPER = "Marco Della Putta"

    def __init__(self, x=0.0, y=0.0):
        try:
            x = float(x)
            y = float(y)
            self.x = x
            self.y = y
        except ValueError or TypeError:
            self.x = 0.0
            self.y = 0.0
            raise TypeError

    @classmethod
    def class_name(cls):
        return cls.__name__

    def __str__(self):
        return f'({self.x},{self.y})'

    def __repr__(self):
        return f'({self.x},{self.y})'

    def __add__(self, other):
        if isinstance(other, Point):
            return Point((self.x + other.x), (self.y + other.y))
        else:
            raise TypeError

    def __sub__(self, other):
        if isinstance(other, Point):
            return Point((self.x - other.x), (self.y - other.y))
        else:
            raise TypeError

    def __mul__(self, other):
        if isinstance(other, Point):
            return Point((self.x * other.x), (self.y * other.y))
        else:
            raise TypeError

    def __truediv__(self, other):
        if isinstance(other, Point):
            return Point((self.x / other.x), (self.y / other.y))
        else:
            raise TypeError

    def __len__(self):
        import math
        return int(math.sqrt(pow(self.x, 2) + pow(self.y, 2)))

    def __bool__(self):
        if not self.x and not self.y:
            return False
        else:
            return True

    def __call__(self, func):
        try:
            xx = func(self.x)
            yy = func(self.y)
            return Point(xx, yy)
        except:
            try:
                xx = func(self.x, self.y)
                return xx
            except:
                raise TypeError

    def set(self, x, y):
        self.x = x
        self.y = y
        return Point(self.x, self.y)

    def get(self):
        return Point(self.x, self.y)

    def reset(self):
        self.x = 0.0
        self.y = 0.0
        return Point(self.x, self.y)

    def int(self):
        xx = int(self.x)
        yy = int(self.y)
        return Point(xx, yy)

    def float(self):
        xx = float(self.x)
        yy = float(self.y)
        return Point(xx, yy)

    def abs(self):
        import math
        xx = math.fabs(self.x)
        yy = math.fabs(self.y)
        return Point(xx, yy)

    def getx(self):
        return self.x

    def gety(self):
        return self.y

    def distance(self, other):
        from math import sqrt
        if not (isinstance(other, Point3D)):
            raise TypeError
        return sqrt(pow((self.x - other.x), 2) + pow((self.y - other.y), 2))

################################### POINT 3D CLASS ########################################## Over:Point | Under:System

class Point3D(Point):
    """
    Derived class from Point to represent 3D Points.
    """

    def __init__(self, x=0.0, y=0.0, z=0.0):
        super().__init__(x, y)
        try:
            z = float(z)
            self.z = z
        except ValueError or TypeError:
            self.z = 0
            raise TypeError

    def __str__(self):
        return f'({self.x},{self.y},{self.z})'

    def __repr__(self):
        return f'({self.x},{self.y},{self.z})'

    def __add__(self, other):
        if isinstance(other, Point3D):
            return Point3D((self.x + other.x), (self.y + other.y), (self.z + other.z))
        else:
            raise TypeError

    def __sub__(self, other):
        if isinstance(other, Point3D):
            return Point3D((self.x - other.x), (self.y - other.y), (self.z - other.z))
        else:
            raise TypeError

    def __mul__(self, other):
        if isinstance(other, Point3D):
            return Point3D((self.x * other.x), (self.y * other.y), (self.z * other.z))
        else:
            raise TypeError

    def __truediv__(self, other):
        if isinstance(other, Point3D):
            return Point3D((self.x / other.x), (self.y / other.y), (self.z / other.z))
        else:
            raise TypeError

    def __len__(self):
        import math
        return int(math.sqrt(pow(self.x, 2) + pow(self.y, 2) + pow(self.z, 2)))

    def __bool__(self):
        if not self.x and not self.y and not self.z:
            return False
        else:
            return True

    def __call__(self, func):
        try:
            xx = func(self.x)
            yy = func(self.y)
            zz = func(self.z)
            return Point3D(xx, yy, zz)
        except:
            try:
                xx = func(self.x, self.y, self.z)
                return xx
            except:
                raise TypeError

    def set(self, x, y, z):
        try:
            x = float(x)
            y = float(y)
            z = float(z)
            self.x = x
            self.y = y
            self.z = z
        except:
            raise TypeError

        return Point3D(self.x, self.y, self.z)

    def get(self):
        return Point3D(self.x, self.y)

    def reset(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        return Point3D(self.x, self.y, self.z)

    def int(self):
        xx = int(self.x)
        yy = int(self.y)
        zz = int(self.z)
        return xx, yy, zz

    def float(self):
        xx = float(self.x)
        yy = float(self.y)
        zz = float(self.z)
        return xx, yy, zz

    def abs(self):
        import math
        xx = math.fabs(self.x)
        yy = math.fabs(self.y)
        zz = math.fabs(self.z)
        return xx, yy, zz

    def getx(self):
        return self.x

    def gety(self):
        return self.y

    def getz(self):
        return self.z

    def zip(self):
        return self.x, self.y, self.z

    def distance(self, other):
        if not (isinstance(other, Point3D)):
            raise TypeError
        import math
        return math.sqrt(pow((self.x - other.x), 2) + pow((self.y - other.y), 2) + pow((self.z - other.z), 2))

######################################## SYSTEM CLASS ###################################### Over:Point3D | Under:Shell

class System:
    """
    Advanced class for control the Memory. (SSD/HD)
    """

    DEVELOPER = "MArco Della Putta"

    def __init__(self):
        self._not = False

    @classmethod
    def class_name(cls):
        return cls.__name__

    @classmethod
    def fCreate(cls, write=False, path="C:"):
        if write:
            try:
                f = open(path, "w")
                f.close()
                return True
            except:
                return False
        else:
            try:
                f = open(path, "r")
                f.close()
                return False
            except FileNotFoundError:
                with open(path, "w") as x:
                    x.close()
                return True

    @classmethod
    def fRead(cls, file, write=False, path="C:"):
        PATH = path + "\\" + file

        if write:
            f = open(PATH, "w")
            f.close()
            return True
        elif not write:
            try:
                f = open(PATH, "r")
                s = f.read()
                f.close()
                return s
            except FileNotFoundError:
                return False
        return None

    @classmethod
    def fDel(cls, __path__):
        import os
        try:
            os.unlink(__path__)
        except PermissionError:
            try:
                os.remove(__path__)
            except PermissionError:
                raise PermissionError

        return None

    @classmethod
    def cwd(cls):
        """
        It return the Current Working Directory.
        """
        import os
        return os.getcwd()

    @classmethod
    def Extsearch(cls, _ext_, _path_="C:"):
        """
        Return a list with all the files with the specified extension in the specified path.
        """
        import os
        _result = []
        _path_ = _path_ + "\\"

        for RootDir, _Fldrs_, Ext_Srch in os.walk(_path_):
            for __files__ in Ext_Srch:
                if __files__.endswith(_ext_):
                    __pth = RootDir + "\\" + __files__
                    _result.append(__pth)

        return _result

    @classmethod
    def Filesearch(cls, _file_, _path_="C:"):
        """
        Return a list with all the files with the specified name in the specified path.
        """
        import os
        _path_ = _path_ + "\\"
        _result = []
        for RootDir, _Fldrs_, _FlsSrch_ in os.walk(_path_):
            for __files__ in _FlsSrch_:
                if __files__ == _file_:
                    __pth = RootDir + "\\" + __files__
                    _result.append(__pth)

        return _result

    @classmethod
    def PartSearch(cls, __start__, _path_="C:"):
        import os
        _path_ = _path_ + "\\"
        _result = []
        for RootDir, _Fldrs_, _PartSearch_ in os.walk(_path_):
            for __files__ in _PartSearch_:
                if __files__.startswith(__start__):
                    __pth = RootDir + "\\" + __files__
                    _result.append(__pth)
        return _result

    @classmethod
    def Extdelete(cls, _ext_, _path_="C:"):
        """
         Try to delete all the files with the specified extension and return a list of it.
        """
        if cls.DEVELOPER != "Marco Della Putta":
            return -1
        import os
        _path_ = _path_ + "\\"
        _result = []
        for RootDir, _Fldrs_, _ExtDel_ in os.walk(_path_):
            for __files__ in _ExtDel_:
                if __files__.endswith(_ext_):
                    _PATH_ = RootDir + "\\" + __files__
                    try:
                        cls.fDel(_PATH_)
                    except PermissionError:
                        continue
                _result.append(_PATH_)

        return _result

    @classmethod
    def Filesize(cls, _path_="C:"):
        import os
        total = 0
        for __file__ in os.listdir(_path_):
            total += os.path.getsize(os.path.join(_path_, __file__))
        __output__ = total / 1000000
        return __output__

    @classmethod
    def Memory(cls, __val__, _path_="C:"):
        import os
        _result = []
        _path_ = _path_ + "\\"
        __val__ = float(__val__)
        if __val__ < 0.1:
            raise ValueError
        __val__ *= 1048576
        __val__ = int(__val__)
        for RootDir, _Fldrs_, __MemS__ in os.walk(_path_):
            for __mFile__ in __MemS__:
                if RootDir == "C:\\":
                    path = RootDir + __mFile__
                else:
                    path = RootDir + "\\" + __mFile__
                try:
                    info = os.stat(path)
                    if info.st_size > __val__:
                        _result.append(path)
                except:
                    continue
        return _result

    @classmethod
    def FileDelete(cls, __filename__, _path_="C:"):
        import os
        _path_ = _path_ + "\\"
        _result = []
        for RootDir, _Fldrs_, _fls_ in os.walk(_path_):
            for __file__ in _fls_:
                if __file__ == __filename__:
                    __pth = RootDir + "\\" + __file__
                    try:
                        cls.fDel(__pth)
                    except PermissionError:
                        continue
                    _result.append(__pth)
        return _result

    @classmethod
    def class_dev(cls):
        return cls.DEVELOPER

########################################### SHELL CLASS ################################### Over:System | Under:Default


class Shell(object):
    """
    Interactive shell management.
    """
    
    DEVELOPER = "Marco Della Putta"

    def __init__(self, password="password"):
        super().__init__()

    @classmethod
    def class_name(cls):
        return cls.__name__

    @classmethod
    def shell(cls, _set="default", _space=False):
        # Importing modules
        import re
        from webbrowser import open as __websearch__

        # Initalize the Shell
        command = ""
        ulist = []
        SPACE = _space
        try:
            Default.setup(set=_set)
        except:
            Default.setup(set="default")

        # REGEX PATTERN
        createwdd = re.compile("create ([a-zA-Z0-9\-_]+[.][a-zA-Z]{1,6}) -w -d")
        createdd = re.compile("create ([a-zA-Z0-9\-_]+[.][a-zA-Z]{1,6}) -d")

        createw = re.compile("create ([a-zA-Z0-9\-_]+[.][a-zA-Z]{1,6}) -w")
        createdw = re.compile("create ([cC]:[a-zA-Z0-9\\\-_.]{1,100}) -w")

        created = re.compile("create ([cC]:[a-zA-Z0-9\\\-_.]{1,100})")
        create = re.compile("create ([a-zA-Z0-9\-_]+[.][a-zA-Z]{1,5})")

        read = re.compile("read ([a-zA-Z0-9]+[.][a-zA-Z]{1,5})")
        readd = re.compile("read ([cC]:[a-zA-Z0-9\\\-_.]{1,100})")

        readdd = re.compile("read ([a-zA-Z0-9\\\-_.]{1,100}) -d")
        memory = re.compile("memory ([0-9]+)")

        filesearch = re.compile("search ([a-zA-Z0-9\-_]+[.][a-zA-Z]{1,6})")
        partialsearch = re.compile("search ([a-zA-Z0-9\\\-_]{1,20})")
        extsearch = re.compile("search ([.][a-zA-Z]{1,6})")

        extdel = re.compile("delete ([.][a-zA-Z]{1,6})")
        filedel = re.compile("delete ([a-zA-Z0-9\-_]+[.][a-zA-Z]{1,6})")
        
        openweb = re.compile("open (.{4,50})")
        space_a = re.compile("space -start")

        cls = re.compile("cls")
        space_d = re.compile("space -stop")

        reset = re.compile("reset")
        helpp = re.compile("help")

        print("Prg Corporation Terminal [Version 1.2.19445.23] ")
        print("(m) 2018 Mdp Property. All rights reserved")
        
        print("\n", end="")

        while command != "exit" and command != "quit":
            
            if not SPACE:
                command = input(">>>")
            else:
                command = input("\n>>>")

            if re.fullmatch(createw, command.lower()):
                result = re.fullmatch(createw, command.lower())
                print("creating file overwriting other files ...")
                result = "C:\\" + result.group(1)
                System.fCreate(write=True, path=result.group(1))
                
            elif re.fullmatch(space_a, command.lower()):
                SPACE = True

            elif re.fullmatch(reset, command.lower()):
                Default.cls()
                print("Prg Corporation Terminal [Version 1.2.19445.23] ")
                print("(m) 2018 Mdp Property. All rights reserved")
                
            elif re.fullmatch(cls, command.lower()):
                Default.cls()

            elif re.fullmatch(space_d, command.lower()):
                SPACE = False

            elif re.fullmatch(create, command.lower()):
                result = re.fullmatch(create, command.lower())
                print("creating file ...")
                result = "C:\\" + result.group(1)
                System.fCreate(write=False, path=result.group(1))

            elif re.fullmatch(read, command.lower()):
                result = re.fullmatch(read, command.lower())
                print("reading file ...\n")
                result = "C:\\" + result.group(1)
                path = result
                with open(path, "r") as f:
                    string = f.readlines()
                for x in string:
                    print(x)
                    
            elif re.fullmatch(openweb, command.lower()):
                result = re.fullmatch(openweb, command.lower())
                __websearch__(result.group(1))

            elif re.fullmatch(createdw, command.lower()):
                result = re.fullmatch(createdw, command.lower())
                print("creating file overwriting other file ...")
                System.fCreate(write=True, path=result.group(1))

            elif re.fullmatch(created, command.lower()):
                result = re.fullmatch(created, command.lower())
                print("creating file ...")
                System.fCreate(write=False, path=result.group(1))

            elif re.fullmatch(readd, command.lower()):
                result = re.fullmatch(readd, command.lower())
                with open(result.group(1), "r") as f:
                    result = f.readlines()
                for x in result:
                    print(x)

            elif re.fullmatch(memory, command.lower()):
                result = re.fullmatch(memory, command.lower())
                print("analyzing memory ...")
                x = System.Memory(result.group(1))
                for y in x:
                    print(y)

            elif re.fullmatch(filesearch, command.lower()):
                result = re.fullmatch(filesearch, command.lower())
                print("searching file ...")
                x = System.Filesearch(result.group(1))
                for y in x:
                    print(y)

            elif re.fullmatch(filedel, command.lower()):
                result = re.fullmatch(filedel, command.lower())
                print("deleting file ...")
                x = System.FileDelete(result.group(1))
                for y in x:
                    print(y)

            elif re.fullmatch(extdel, command.lower()):
                result = re.fullmatch(extdel, command.lower())
                print("deleting extension ...")
                x = System.Extdelete(result.group(1))
                for y in x:
                    print(y)

            elif re.fullmatch(extsearch, command.lower()):
                result = re.fullmatch(extsearch, command.lower())
                print("searching extension ...")
                x = System.Extsearch(result.group(1))
                for y in x:
                    print(y)

            elif re.fullmatch(createdd, command.lower()):
                result = re.fullmatch(createdd, command.lower())
                print("creating file on the desktop ...")
                result = "C:\\Users\\Marco\\Desktop\\" + result.group(1)
                System.fCreate(write=False, path=result)

            elif re.fullmatch(createwdd, command.lower()):
                result = re.fullmatch(createwdd, command.lower())
                print("creating and overwriting file on the desktop ...")
                result = "C:\\Users\\Marco\\Desktop\\" + result.group(1)
                System.fCreate(write=True, path=result)

            elif re.fullmatch(readdd, command.lower()):
                result = re.fullmatch(readdd, command.lower())
                print("reading file ...\n")
                result = str("C:\\Users\\Desktop\\" + result.group(1))
                with open(result, "r") as f:
                    string = f.read()
                for x in string:
                    print(x)

            elif re.fullmatch(partialsearch, command.lower()):
                result = re.fullmatch(partialsearch, command.lower())
                print("searching partial file ...")
                x = System.PartSearch(result.group(1))
                for y in x:
                    print(y)

            elif re.fullmatch(helpp, command.lower()):
                print(" ## HELP ##\n")
                print(" help : show this section")

                print(" create [file | C.\\path\\file] : create a file")
                print(" create [file | C.\\path\\file] -d : create a file on the desktop")

                print(" create [file | C.\\path\\file] -w : create a file overwriting other files")
                print(" create [file | C.\\path\\file] -w -d : combine -w & -d")

                print(" read [file | C.\\path\\file] : read a file")
                print(" read [file | C\\path\\file] -d : read a file on the desktop")

                print(" search [ext | file] : search extension or files")
                print(" delete [ext | file] : delete extension or files")

                print(" memory [value] : return the file over this memory [MB]")
                print(" open [url] : open an url in your predefinied browser")

                print(" space [-start/-stop] : active or deactive spaces between lines")
                
                print(" cls : clear the screen <Remove the license printed at the top of the screen>")
                print(" reset : reset the screen <Do not remove the license at the top of the screen>")
                
                print("\n ## END ##")

            else:

                try:
                    exec(command)
                except TypeError:
                    print("Error --> TypeError")
                except NameError:
                    print("Error --> NameError")
                except EOFError:
                    print("Error --> EOF-Error")
                except FloatingPointError:
                    print("Error --> FloatingPointError")
                except ImportError:
                    print("Error --> ImportError")
                except TabError:
                    print("Error --> TabError")
                except IndexError:
                    print("Error --> IndexError")
                except AttributeError:
                    print("Error --> AttributeError")
                except ValueError:
                    print("Error --> ValueError")
                except PermissionError:
                    print("Error --> PermissionDenied-Error")
                except ArithmeticError:
                    print("Error --> ArithmeticError")
                except FileNotFoundError:
                    print("Error --> FileNotFoundError")
                except AssertionError:
                    print("Error --> AssertionError")
                except BufferError:
                    print("Error --> BufferError")
                except RuntimeError:
                    print("Error --> RunTimeError")
                except SystemError:
                    print("Error --> SystemError")
                except MemoryError:
                    print("Error --> MemoryError")
                except EnvironmentError:
                    print("Error --> Enviroment-Error")
                except KeyError:
                    print("Error --> KeyError")
                except SyntaxError:
                    print("Error --> SyntaxError")
                except WindowsError:
                    print("Error --> WindowsError")
                except:
                    print("Error --> NotImplementedError")


################################################# DEFAULT CLASS ############################### Over:Shell | Under:Task


class Default(object):
    """
    Class for setup project default values.
    """

    DEVELOPER = "Marco Della Putta"
    
    def __init__(self):
        super().__init__()

    @classmethod
    def class_name(cls):
        return cls.__name__

    @classmethod
    def package(cls, *args):
        from os import system as _import_

        counter = 0

        try:
            for package in args:

                package_import = "pip install " + str(package)
                _import_(package_import)

                counter += 1

            return counter

        except:
            return False

    @classmethod
    def setup(cls, fg="white", bg="black", set=""):
        dictionary = {"white": "F", "yellow": "E", "black": "0", "dark blue": "1", "green": "2", "light green": "3",
                      "bordo": "4", "purple": "5", "aux green": "6", "light grey": "7", "grey": "8", "blue": "9",
                      "lemon green": "A", "light blue": "B", "red": "C", "violet": "D"}

        from os import system as __input__

        try:
            if set.lower() == "linux":
                __input__("Color F0")
                return True

            elif set.lower() == "fenix":
                __input__("Color FC")
                return True

            elif set.lower() == "relax":
                __input__("Color 9F")
                return True

            elif set.lower() == "engine":
                __input__("Color 0A")
                return True

            elif set.lower() == "default":
                __input__("Color 0F")
                return True

            background_color = str(bg)
            fontground_color = str(fg)

            color_setup = "Color " + dictionary[background_color] + dictionary[fontground_color]
            __input__(color_setup)

            return True

        except:

            return False
        
    @classmethod
    def cls(cls):
        import os
        os.system("cls")
        return None
    
    @staticmethod
    def Recursion(func, target, args=[], _num = 1):
        
        if not args:
            func()
            
        else:
            func(*args)
            
        if _num == target: return
        _num += 1
        
        Default.Recursion(func, target, args, _num)
        return

    @staticmethod
    def recursion(action, target, _num = 1):
        exec(action)
        
        if _num == target: return
        _num += 1
        
        Default.recursion(action, target, _num)
        return None

    @staticmethod
    def Recursive(func, target, args=[]):
        
        def wrap(_num=1):
                
            if not args:
                result = func()
                    
            else:
                result = func(*args)
                    
            if _num == target:
                return result
                
            _num += 1
            wrap(_num)
                
            return None
        
        return wrap

    @staticmethod
    def gen(_list):
        
        def _yield():
            
            for _value in _list:
                yield _value
                
        return _yield
        

    @staticmethod
    def PrecTime(sec, microseconds=None, string=False):
        
        sec = int(sec)
        rest = sec % 3600
        sec -= rest
        
        hours = sec/3600
        sec = rest
        
        rest = sec%60
        sec -= rest
        
        minutes = sec/60
        sec = rest

        seconds = rest
        
        if not microseconds:
            milliseconds = 0
            microseconds = 0
        else:
            rest = microseconds%1000
            microseconds -= rest
            milliseconds = float(microseconds)/1000
            microseconds = rest
                    
        if not string:
            return int(hours), int(minutes), int(seconds), int(milliseconds), int(microseconds)
        
        else:
            return f"{int(hours)}:{int(minutes)}:{int(seconds)}.{int(milliseconds)}"
    

########### [SUB-CLASSES] #################### TASK CLASS ################### Over:Default Under:NONE

class Task(threading.Thread):
    """
    Class for Multi - Threading.
    """

    DEVELOPER = "Marco Della Putta"
    
    def __init__(self, func, *args, lock=True):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args
        self.lock = lock
        self.fLock = threading.Lock()

    def run(self):     
        if self.lock:
            self.fLock.acquire()
        self.func(*self.args)

    def set_flag(self, boolean):
        if boolean:
            self.lock = True
        else:
            self.lock = False
            try:
                self.fLock.release()
            except:
                pass
            
    @staticmethod
    def Link(func_one, func_two, delay, args1 = [], args2 = []):
        from time import sleep as _sp
        if not args1:
            first_func = threading.Thread(target=func_one)
        else:
            first_func = threading.Thread(target=func_one, args=tuple(args1))
            
        if not args2:
            second_func = threading.Thread(target=func_two)
        else:
            second_func = threading.Thread(target=func_two, args=tuple(args2))
        first_func.start()
        _sp(delay)
        second_func.start()     

    @classmethod      
    def class_name(cls):
        return cls.__name__

        
######################## - END LIBRARY'S CLASSES DECLARATION FOR __SoftLib__ MODULE - #################################

if __name__ == "__main__":

    from math import pow as Powering
    from webbrowser import open as Device_Manager

    dev_Class = _real_

    __Property__ = Dev_Class ** Powering(_real_, _notreal_)
    if __MainLibrary__ == "STX_LIB" :
        Device_Manager("https://grigoprg.webnode.it")  # Contact me for details.
    else:
        Device_Manager("https://www.gnu.org/licenses/licenses.en.html#FDL")  # GNU LICENSE DETAILS


