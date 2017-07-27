# -*- coding: utf-8 -*-
"""
Created on Mon Jan 30 14:18:48 2017

This module contains all the categories and the dicts associated with them.

@author: Robert Morton
"""

from utils import Category, MatchPhase
import Algorithm as al
import scaled_scouting_si as sssi
import var_n_binomial_si as vnbs

FOULS = Category(MatchPhase.BOTH, 'fouls', 'foulCount')
TECH_FOULS = Category(MatchPhase.BOTH, 'tech fouls', 'techFoulCount')

SCENARIOS_FROM_YEARS = {'2016':(), '2017':('elims')}

#stronghold
STRONGHOLD_AUTON_LOW_BOULDERS = Category(MatchPhase.AUTON, 'auton low boulders', 'autoBouldersLow')
STRONGHOLD_AUTON_HIGH_BOULDERS = Category(MatchPhase.AUTON, 'auton high boulders', 'autoBouldersHigh')
STRONGHOLD_TELEOP_LOW_BOULDERS = Category(MatchPhase.TELEOP, 'teleop low boulders', 'teleopBouldersLow')
STRONGHOLD_TELEOP_HIGH_BOULDERS = Category(MatchPhase.TELEOP, 'teleop high boulders', 'teleopBouldersHigh')

STRONGHOLD_CATEGORIES = (STRONGHOLD_AUTON_LOW_BOULDERS,
                         STRONGHOLD_AUTON_HIGH_BOULDERS,
                         STRONGHOLD_TELEOP_LOW_BOULDERS,
                         STRONGHOLD_TELEOP_HIGH_BOULDERS)
STRONGHOLD_ALGORITHMS = {STRONGHOLD_AUTON_LOW_BOULDERS:al.get_team_prob_distrs,#al for all
                         STRONGHOLD_AUTON_HIGH_BOULDERS:al.get_team_prob_distrs,
                         STRONGHOLD_TELEOP_LOW_BOULDERS:al.get_team_prob_distrs,
                         STRONGHOLD_TELEOP_HIGH_BOULDERS:al.get_team_prob_distrs}
#STRONGHOLD_ALGORITHMS = {STRONGHOLD_AUTON_LOW_BOULDERS:vnbs.bound_with_ratio_stdev(.1),
#                         STRONGHOLD_AUTON_HIGH_BOULDERS:vnbs.bound_with_ratio_stdev(.1),
#                         STRONGHOLD_TELEOP_LOW_BOULDERS:vnbs.bound_with_ratio_stdev(.1),
#                         STRONGHOLD_TELEOP_HIGH_BOULDERS:vnbs.bound_with_ratio_stdev(.1)}
#STRONGHOLD_FILL_SCOUTS = {STRONGHOLD_AUTON_LOW_BOULDERS:al.null_fill_scouting,#al for all
#                         STRONGHOLD_AUTON_HIGH_BOULDERS:al.null_fill_scouting,
#                         STRONGHOLD_TELEOP_LOW_BOULDERS:al.null_fill_scouting,
#                         STRONGHOLD_TELEOP_HIGH_BOULDERS:al.null_fill_scouting}
STRONGHOLD_FILL_SCOUTS = {STRONGHOLD_AUTON_LOW_BOULDERS:al.fill_scouting,#al for all
                         STRONGHOLD_AUTON_HIGH_BOULDERS:al.fill_scouting,
                         STRONGHOLD_TELEOP_LOW_BOULDERS:al.fill_scouting,
                         STRONGHOLD_TELEOP_HIGH_BOULDERS:al.fill_scouting}
#end stronghold

#steamworks
STEAMWORKS_AUTON_LOW_FUEL = Category(MatchPhase.AUTON, 'auton low fuel', 'autoFuelLow')
STEAMWORKS_AUTON_HIGH_FUEL = Category(MatchPhase.AUTON, 'auton high fuel', 'autoFuelHigh')
STEAMWORKS_AUTON_GEARS = Category(MatchPhase.AUTON, 'auton gears', 'autoGears')
STEAMWORKS_AUTON_BASELINE = Category(MatchPhase.AUTON, 'crossed baseline', 'crossedBaseline')

STEAMWORKS_TELEOP_LOW_FUEL = Category(MatchPhase.TELEOP, 'teleop low fuel', 'teleopFuelLow')
STEAMWORKS_TELEOP_HIGH_FUEL = Category(MatchPhase.TELEOP, 'teleop high fuel', 'teleopFuelHigh')
STEAMWORKS_TELEOP_GEARS = Category(MatchPhase.TELEOP, 'teleop gears', 'teleopGears')
STEAMWORKS_TELEOP_HANGING = Category(MatchPhase.TELEOP, 'hanging', 'teleopHung')

STEAMWORKS_CATEGORIES = (STEAMWORKS_AUTON_LOW_FUEL,
                         STEAMWORKS_AUTON_HIGH_FUEL,
                         STEAMWORKS_AUTON_GEARS,
                         STEAMWORKS_AUTON_BASELINE,
                         STEAMWORKS_TELEOP_LOW_FUEL,
                         STEAMWORKS_TELEOP_HIGH_FUEL,
                         STEAMWORKS_TELEOP_GEARS,
                         STEAMWORKS_TELEOP_HANGING,
                         FOULS,
                         TECH_FOULS)
STEAMWORKS_ALGORITHMS = {STEAMWORKS_AUTON_LOW_FUEL:sssi.get_stack_indiv_distrs,
                         STEAMWORKS_AUTON_HIGH_FUEL:sssi.get_stack_indiv_distrs,
                         STEAMWORKS_AUTON_GEARS:sssi.get_bernoulli_stack_indiv_distrs,
                         STEAMWORKS_AUTON_BASELINE:sssi.get_bernoulli_stack_indiv_distrs,
                         STEAMWORKS_TELEOP_LOW_FUEL:sssi.get_stack_indiv_distrs,
                         STEAMWORKS_TELEOP_HIGH_FUEL:sssi.get_stack_indiv_distrs,
                         STEAMWORKS_TELEOP_GEARS:sssi.get_stack_indiv_distrs,
                         STEAMWORKS_TELEOP_HANGING:sssi.get_bernoulli_stack_indiv_distrs,
                         FOULS:sssi.get_stack_indiv_distrs,
                         TECH_FOULS:sssi.get_stack_indiv_distrs}
STEAMWORKS_FILL_SCOUTS = {STEAMWORKS_AUTON_LOW_FUEL:al.null_fill_scouting,
                         STEAMWORKS_AUTON_HIGH_FUEL:al.null_fill_scouting,
                         STEAMWORKS_AUTON_GEARS:al.null_fill_scouting,
                         STEAMWORKS_AUTON_BASELINE:al.null_fill_scouting,
                         STEAMWORKS_TELEOP_LOW_FUEL:al.null_fill_scouting,
                         STEAMWORKS_TELEOP_HIGH_FUEL:al.null_fill_scouting,
                         STEAMWORKS_TELEOP_GEARS:al.null_fill_scouting,
                         STEAMWORKS_TELEOP_HANGING:al.null_fill_scouting,
                         FOULS:al.null_fill_scouting,
                         TECH_FOULS:al.null_fill_scouting}
#end steamworks