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


# examples of consecutive cores for SMTS.
# a(k_coverees1([3, 3, 2, 2, 1, 1], 2), set([Partition([3, 2, 2, 1, 1])]))
# a(k_coverees1([2, 2, 1, 1], 2), set([Partition([2, 1, 1])]))
# a(k_coverees1([2, 1, 1], 2), set([Partition([2]), Partition([1, 1])]))
# a(k_coverees1([6, 4, 2, 2, 1], 5), set([Partition([5, 4, 2, 2, 1]), Partition([6, 2, 2, 2, 1]), Partition([6, 3, 2, 2]), Partition([6, 4, 2, 1, 1])]))

# SkewPartitions.options(diagram_str='#', convention='French')
# def go(outer_core, k):
# 	coverees = k_coverees(outer_core, k)
# 	for coveree in coverees:
# 		sp = SkewPartition([outer_core, coveree])
# 		print(ascii_art(sp))
# 		print('-------------')

# go([2, 1, 1], 2)
# go([6, 4, 2, 2, 1], 5)
# go([3, 3, 2, 2, 1, 1], 2)


k = 2
core = Partition([1])
coverees = k_coverees(core, k)
for coveree in coverees:
	print(coveree)




# ALL DONE!
print('Local code completed successfully!', end='')
end_time = time.time()
elapsed_time = end_time - start_time
print(' Elapsed time = {}'.format(elapsed_time))
