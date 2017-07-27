#from ZScout import *
from utils import SegmentMatch
import MatchEvaluators as me
import categories as ct
#import Blue_Alliance_API

def stronghold_segment(match):
    def partial_segment(number, score_breakdown, teams):
        result = {}
        result[ct.STRONGHOLD_TELEOP_LOW_BOULDERS] = SegmentMatch(number, ct.STRONGHOLD_TELEOP_LOW_BOULDERS, score_breakdown[ct.STRONGHOLD_TELEOP_LOW_BOULDERS.tba_name], teams)
        result[ct.STRONGHOLD_TELEOP_HIGH_BOULDERS] = SegmentMatch(number, ct.STRONGHOLD_TELEOP_HIGH_BOULDERS, score_breakdown[ct.STRONGHOLD_TELEOP_HIGH_BOULDERS.tba_name], teams)
        result[ct.STRONGHOLD_AUTON_LOW_BOULDERS] = SegmentMatch(number, ct.STRONGHOLD_AUTON_LOW_BOULDERS, score_breakdown[ct.STRONGHOLD_AUTON_LOW_BOULDERS.tba_name], teams)
        result[ct.STRONGHOLD_AUTON_HIGH_BOULDERS] = SegmentMatch(number, ct.STRONGHOLD_AUTON_HIGH_BOULDERS, score_breakdown[ct.STRONGHOLD_AUTON_HIGH_BOULDERS.tba_name], teams)
        return result
    
    blue_teams = match['alliances']['blue']['teams']
    red_teams = match['alliances']['red']['teams']
    result = []
    number = match['match_number']
    breakdown = match['score_breakdown']
    result.append(partial_segment(number, breakdown['blue'], blue_teams))
    result.append(partial_segment(number, breakdown['red'], red_teams))
    return result

def steamworks_segment(match):
    def baseline_segment(number, score_breakdown, teams):
        baseline = 0
        for key in ('robot1Auto', 'robot2Auto', 'robot3Auto'):
            if score_breakdown[key] == 'Mobility':
                baseline += 1
                
        return SegmentMatch(number, ct.STEAMWORKS_AUTON_BASELINE, baseline, teams)
    
    def hanging_segment(number, score_breakdown, teams):
        hanging = 0
        for key in ('touchpadNear', 'touchpadMiddle', 'touchpadFar'):
            if score_breakdown[key] == 'Engaged':
                hanging += 1
                
        return SegmentMatch(number, ct.STEAMWORKS_TELEOP_HANGING, hanging, teams)
    
    def gears_segment(number, score_breakdown, teams):
        auton_rotors = 0
        if score_breakdown['rotor1Auto']:
            auton_rotors += 1
        if score_breakdown['rotor2Auto']:
            auton_rotors += 1
            
        auton_min = me.GEAR_TOTALS[auton_rotors - 1] if auton_rotors >= 1 else 0
        auton_max = min(3, me.GEAR_TOTALS[auton_rotors] - 1)
            
        teleop_rotors = 0
        if score_breakdown['rotor1Engaged']:
            teleop_rotors += 1
        if score_breakdown['rotor2Engaged']:
            teleop_rotors += 1
        if score_breakdown['rotor3Engaged']:
            teleop_rotors += 1
        if score_breakdown['rotor4Engaged']:
            teleop_rotors += 1
           
        teleop_min = 0
        teleop_max = None
        if auton_max != None:
            teleop_min = max(0, (me.GEAR_TOTALS[teleop_rotors - 1] if teleop_rotors >= 1 else 0) - auton_max - 1) #reserve gear
            teleop_max = (me.GEAR_TOTALS[teleop_rotors] - 1 - auton_min) if (teleop_rotors < 4) else None
            if teleop_max != None:
                teleop_max = max(0, teleop_max)
            
        auton_match = SegmentMatch(number, ct.STEAMWORKS_AUTON_GEARS, None, teams, minimum=auton_min, maximum=auton_max)
        teleop_match = SegmentMatch(number, ct.STEAMWORKS_TELEOP_GEARS, None, teams, minimum=teleop_min, maximum=teleop_max)
    
        return auton_match, teleop_match
    
    def partial_segment(number, score_breakdown, teams):
        
        gears_matches = gears_segment(number, score_breakdown, teams)
        
        result = {}
        result[ct.STEAMWORKS_AUTON_LOW_FUEL] = SegmentMatch(number, ct.STEAMWORKS_AUTON_LOW_FUEL, score_breakdown[ct.STEAMWORKS_AUTON_LOW_FUEL.tba_name], teams)
        result[ct.STEAMWORKS_AUTON_HIGH_FUEL] = SegmentMatch(number, ct.STEAMWORKS_AUTON_HIGH_FUEL, score_breakdown[ct.STEAMWORKS_AUTON_HIGH_FUEL.tba_name], teams)
        result[ct.STEAMWORKS_AUTON_GEARS] = gears_matches[0]
        result[ct.STEAMWORKS_AUTON_BASELINE] = baseline_segment(number, score_breakdown, teams)
        result[ct.STEAMWORKS_TELEOP_LOW_FUEL] = SegmentMatch(number, ct.STEAMWORKS_TELEOP_LOW_FUEL, score_breakdown[ct.STEAMWORKS_TELEOP_LOW_FUEL.tba_name], teams)
        result[ct.STEAMWORKS_TELEOP_HIGH_FUEL] = SegmentMatch(number, ct.STEAMWORKS_TELEOP_HIGH_FUEL, score_breakdown[ct.STEAMWORKS_TELEOP_HIGH_FUEL.tba_name], teams)
        result[ct.STEAMWORKS_TELEOP_GEARS] = gears_matches[1]
        result[ct.STEAMWORKS_TELEOP_HANGING] = hanging_segment(number, score_breakdown, teams)
        result[ct.FOULS] = SegmentMatch(number, ct.FOULS, score_breakdown[ct.FOULS.tba_name], teams)
        result[ct.TECH_FOULS] = SegmentMatch(number, ct.TECH_FOULS, score_breakdown[ct.TECH_FOULS.tba_name], teams)
        
        return result

    blue_teams = match['alliances']['blue']['teams']
    red_teams = match['alliances']['red']['teams']
    result = []
    number = match['match_number']
    breakdown = match['score_breakdown']
    result.append(partial_segment(number, breakdown['blue'], blue_teams))
    result.append(partial_segment(number, breakdown['red'], red_teams))
    return result