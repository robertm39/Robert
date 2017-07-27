# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 19:09:04 2017

@author: rober
"""

import sympy as sm

import distrs as di

sm.init_printing()

x = sm.symbols('x', real=True)
m = 5
v = 0.001
p = 1

var_n_bino = di.var_n_binomial(x, m, v, p)
#display(var_n_bino)
for i in range(0, 1):
    subst = var_n_bino.subs(x, i)
    print(var_n_bino.free_symbols)
    print(subst.free_symbols)
    subst = subst.subs(list(subst.free_symbols)[0], 1)
    print(subst.free_symbols)
    print(i)
    #display(subst)
    print('')