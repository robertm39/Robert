# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 17:18:11 2017

@author: rober
"""

import categories as ctgs
import scoutingdatagetters as sdg
import MatchSegmenters as ms
import MatchEvaluators as me
import Predictor as pd

class Game:
    
    def __init__(self, year, scenarios, categories, scouting_data_types, get_data_from_match, algorithms_from_categories, fill_scout_from_categories,  segment, evaluate, predict):
        self.year = year
        self.scenarios = scenarios
        self.categories = categories
        self.scouting_data_types = scouting_data_types
        self.get_data_from_match = get_data_from_match
        self.algorithms_from_categories = algorithms_from_categories
        self.fill_scout_from_categories = fill_scout_from_categories
        self.segment = segment
        self.evaluate = evaluate
        self.predict = predict
        
STRONGHOLD = Game('2016', tuple([]), ctgs.STRONGHOLD_CATEGORIES, None, None, ctgs.STRONGHOLD_ALGORITHMS, ctgs.STRONGHOLD_FILL_SCOUTS, ms.stronghold_segment, me.evaluate_stronghold_match, pd.enumerate_predict_match)
#STEAMWORKS = Game('2017', tuple(['elims']), ctgs.STEAMWORKS_CATEGORIES, ('auton_lowgoal', 'auton_highgoal', 'rgt_auton_gears', 'cen_auton_gears', 'lft_auton_gears', 'crossed_baseline', 'teleop_lowgoal', 'teleop_highgoal', 'teleop_gears', 'hanging', 'comments'), sdg.get_steamworks_data, ctgs.STEAMWORKS_ALGORITHMS, ctgs.STEAMWORKS_FILL_SCOUTS, ms.steamworks_segment, me.evaluate_steamworks_match, pd.smart_predict_match_trials_bound(gen_trials=100000, enum_trials=5000))#gen_trials=50000, enum_trials=10000))
STEAMWORKS = Game('2017', tuple(['elims']), ctgs.STEAMWORKS_CATEGORIES, ('auton_lowgoal', 'auton_highgoal', 'rgt_auton_gears', 'cen_auton_gears', 'lft_auton_gears', 'crossed_baseline', 'teleop_lowgoal', 'teleop_highgoal', 'teleop_gears', 'hanging', 'comments'), sdg.get_steamworks_data, ctgs.STEAMWORKS_ALGORITHMS, ctgs.STEAMWORKS_FILL_SCOUTS, ms.steamworks_segment, me.evaluate_steamworks_match, pd.enumerate_predict_match)#gen_trials=50000, enum_trials=10000))
GAMES_FROM_YEARS = {'2016':STRONGHOLD, '2017':STEAMWORKS}