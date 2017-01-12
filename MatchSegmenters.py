#from ZScout import *
from ScoreReq import ScoreReq
from MatchPhase import MatchPhase
from SegmentMatch import SegmentMatch
from Category import Category
#import Blue_Alliance_API

def stronghold_segment(match):
    def partial_segment(number, score_breakdown, teams):
        result = {}
        teleop_low_goal_category = Category(True, ScoreReq.INDIVIDUAL, MatchPhase.TELEOP, 'teleop low goal')
        result[teleop_low_goal_category] = SegmentMatch(number, teleop_low_goal_category, score_breakdown['teleopBouldersLow'], teams)
        
        teleop_high_goal_category = Category(True, ScoreReq.INDIVIDUAL, MatchPhase.TELEOP, 'teleop high goal')
        result[teleop_high_goal_category] = SegmentMatch(number, teleop_high_goal_category, score_breakdown['teleopBouldersHigh'], teams)
        
        auton_low_goal_category = Category(True, ScoreReq.INDIVIDUAL, MatchPhase.AUTON, 'auton low goal')
        result[auton_low_goal_category] = SegmentMatch(number, auton_low_goal_category, score_breakdown['autoBouldersLow'], teams)
        
        auton_high_goal_category = Category(True, ScoreReq.INDIVIDUAL, MatchPhase.AUTON, 'auton high goal')
        result[auton_high_goal_category] = SegmentMatch(number, auton_high_goal_category, score_breakdown['autoBouldersHigh'], teams)
        return result
    
    blue_teams = match['alliances']['blue']['teams']
    red_teams = match['alliances']['red']['teams']
    result = []
    number = match['match_number']
    breakdown = match['score_breakdown']
    result.append(partial_segment(number, breakdown['blue'], blue_teams))
    result.append(partial_segment(number, breakdown['red'], red_teams))
    return result

