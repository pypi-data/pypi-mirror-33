

from lab10.conv import *
from lab10.solv import *

try:
    a=int(input('A:'))
    b=int(input('B:'))
    c=int(input('C:'))
except ValueError:
    print("Not a number")

print("f(x)=" + str(a) + "x^2 + " + str(b) + "x + " + str(c))
if calculatedelta(a, b, c) < 0:
    print("No solutions found")
else:
    print("Solution 1: x=" + str(getsolution1(a,b,c)))
    print("Solution 2: x=" + str(getsolution2(a,b,c)))
