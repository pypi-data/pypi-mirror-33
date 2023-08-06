# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 16:21:01 2018

@author: erwan
"""

from radis import load_spec
from radis.test.utils import getTestFile
import os

s = load_spec(getTestFile('CO_Tgas1500K_mole_fraction0.5.spec'))
#s.populations
assert not os.path.exists('CO_without_populations.spec') 
try:
    s.store('CO_without_populations.spec', compress=True, discard=['lines', 'populations'])
    s2 = load_spec('CO_without_populations.spec')
finally:
    pass
#    os.remove('CO_without_populations.spec')

# Now let's test: normally s2 has no population
assert len(s2.populations)==0

