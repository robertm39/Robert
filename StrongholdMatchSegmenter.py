#from ZScout import *
from ScoreReq import ScoreReq
from MatchPhase import MatchPhase
from SegmentMatch import SegmentMatch
from Category import Category
#import Blue_Alliance_API

class StrongholdMatchSegmenter:

    def segment(self, match):
        blue_teams = match['alliances']['blue']['teams']
        red_teams = match['alliances']['red']['teams']
        result = []
        number = match['match_number']
        breakdown = match['score_breakdown']
        result.append(self.partial_segment(number, breakdown['blue'], blue_teams))
        result.append(self.partial_segment(number, breakdown['red'], red_teams))
        return result

    def partial_segment(self, number, score_breakdown, teams):
        result = {}
        teleop_low_goal_category = Category(1, ScoreReq.INDIVIDUAL, MatchPhase.TELEOP, 'teleop low goal')
        result[teleop_low_goal_category] = SegmentMatch(number, teleop_low_goal_category, score_breakdown['teleopBouldersLow'], teams)

        teleop_high_goal_category = Category(1, ScoreReq.INDIVIDUAL, MatchPhase.TELEOP, 'teleop high goal')
        result[teleop_high_goal_category] = SegmentMatch(number, teleop_high_goal_category, score_breakdown['teleopBouldersHigh'], teams)
        return result
        
