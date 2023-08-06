Always wanted to add custom operators ?

    a = (1,2,3) /dot/ (4,5,6) # a = 32

Works for existing functions, like `numpy.dot`

    import numpy
    dot = infix(numpy.dot)
    a = (1,2,3) /dot/ (4,5,6) # use as an infix
    a = dot((1,2,3), (4,5,6)) # still works as a function

Or for custom functions as a decorator

    @infix
    def f(x,y):
        return x + 2 * y

    a = 1 |f| 2 # operator, can use any binary operator like / | * % << >> (beware of ** that is right to left)
    a = f(1, 2) # function

## dot and cross product

    a = (1,2,3) /dot/ (4,5,6) # use as an infix
    a = (1,2,3) |dot| (4,5,6) # can use any binary operator like / | * % << >> (beware of ** that is right to left)
    r = 2 + (1,2,3) /dot/ (4,5,6) # here "/" has priority over + like in normal python
    r = 2 + (1,2,3) *dot* (4,5,6) # for a dot PRODUCT, * seems logical
    r = 2 + dot((1,2,3), (4,5,6)) # still works as a function

## using '|' for low priority

    A + B |dot| C # is parsed as (A + B) |dot| C

## fractions

    from fractions import Fraction
    frac = infix(Fraction)
    a = 1 + 1 / 3      # floats are messy...
    a = 1 + 1 /frac/ 3 # just replace '/' by '/frac/' to use Fractions
    b = 2 * (a + 3) /frac/ (a + 1) # nicer complex expressions

## ranges, 2..5 in ruby ?

    @infix
    def inclusive(a,b):
        return range(a, b+1)

    for i in 2 /inclusive/ 5: # could also write |inclusive| or +inclusive+ or %inclusive% or 
        print(i) # 2 3 4 5

    for i in inclusive(2, 5): # can still be used as function
        print(i) # 2 3 4 5

## pipes : postfix

    @postfix
    def no_zero(L):
        return [x for x in L if x != 0]

    @postfix
    def plus_one(L):
        return [x+1 for x in L]

    Y = [1,2,7,0,2,0] |no_zero |plus_one # Y == [2,3,8,3]
    Y = plus_one(no_zero([1,2,7,0,2,0])) # Y == [2,3,8,3]

## pipe factory

    def filter_out(x):
        @postfix
        def f(L):
            return [y for y in L if y != x]
        return f

    L = [1,2,7,0,2,0] | filter_out(0)

## function compose

    s = hex(ord('A')) # s = '0x41'

    from funcoperators import compose
    display = hex /compose/ ord
    s = display('A') # s = '0x41'

    f = hex *circle* ord # circle = compose

## partial syntax

    def f(x,y):
        return x + y
    
    from funcoperators import curry
    g = f /curry/ 5
    y = f(2) # y = 7

    from funcoperators import partially
    @partially
    def f(x,y,z):
        return x + y + z

    r = f(1,2,3)
    r = f[1](2,3)
    r = f[1][2][3]()
    # NOT: f[1,2] which will give one argument: a tuple

# partiallyauto works only for methods with N fixed positional args

    @partiallyauto
    def f(x,y,z):
        return x + y + z

    r = f(1,2,3)   # r = 6
    r = f(1)(2)(3) # r = 6
    r = f(1)(2,3)  # r = 6
    g = f(1)   # g = a function with two arguments 
    r = g(2,3) # r= 6
    k = g(2)   # k = a function with one argument

# see more examples in the test cases in source code
