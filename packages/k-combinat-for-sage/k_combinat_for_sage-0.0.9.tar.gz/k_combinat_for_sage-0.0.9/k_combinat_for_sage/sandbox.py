#!/usr/bin/env sage
# Just a place to quickly test things.  NOT part of repo.
from __future__ import print_function
import time
from sage.all import *
from testing import *
from all import *
start_time = time.time()
print('Sage loaded.  Executing stuff...')
# BEGIN!


v = [1, 1, 1]
print(v)
rv = r_func(v)
print(rv)
x = var('x')
mon = x**2
print(mon)
funced_mon = call_me_monomial(mon.coefficients()[0], v)
print(funced_mon)
exp = 3 + x
print(exp)
funced_exp = call_me(exp, v)
print(funced_exp)




# test hall littlewood verter op
# Sym = SymmetricFunctions(QQ['t'])
# gamma_lis = [2, 1, 1]
# gamma = Partition(gamma_lis)
# hop = HallLittlewoodVertexOperator(gamma)
# one = Sym.one()
# hl_poly_maybe = hop(one)
# s = Sym.s()
# hl = Sym.hall_littlewood().P() # more than one type of 'hall littlewood'.  we use the P basis.
# hl_poly = hl[gamma_lis]
# print('my hall littlewood')
# print(s(hl_poly_maybe))
# print(hl(hl_poly_maybe))
# print('actual hall littlewood')
# print(s(hl_poly))
# print(hl(hl_poly))




# ALL DONE!
print('Local code completed successfully!', end='')
end_time = time.time()
elapsed_time = end_time - start_time
print(' Elapsed time = {}'.format(elapsed_time))
