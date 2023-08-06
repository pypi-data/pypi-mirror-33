########################################## CLASS EXPRESSION ################################### Over:License | Under:Shell

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
