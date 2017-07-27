# -*- coding: utf-8 -*-
"""
Created on Sun Apr  2 13:42:10 2017

@author: rober
"""

from mc_utils import MultiMergeIterator

l1 = [0, 1, 2, 3]
l2 = [1, 2, 3, 4]#[1, 2, 3, 4]

iterator = MultiMergeIterator(lambda a: a, iter(l1), iter(l2))

print(iterator.__next__())
print(iterator.__next__())
print(iterator.__next__())

l3 = [6, 8, 10]
l4 = [7, 9]

print('adding iterators')
iterator.add_iterator(iter(l3))
iterator.add_iterator(iter(l4))

while True:
    try:
        print(iterator.__next__())
    except StopIteration:
        break