# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 17:48:55 2017

@author: rober
"""

import comp as cp
import games as gms

week0 = cp.get_competition('2017week0')[0]
#print(week0)
#for match in week0:
#    print(match)
#    print('')
#print('')
segmenter = gms.STEAMWORKS.segment
segmented = cp.segment_competition(week0, segmenter)
for category in segmented:
    segmented_comp = segmented[category]
    print(category)
    for segment_match in segmented_comp:
        print(segment_match)
    print('')