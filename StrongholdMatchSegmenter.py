#from ZScout import *
import utils as ut
import categories as cts

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
#        result = {}
#        
#        result[cts.STRONGHOLD_AUTON_LOW_BOULDERS] = SegmentMatch(number, cts.STRONGHOLD_AUTON_LOW_BOULDERS, score_breakdown['teleopBouldersLow'], teams)
#
#        result[cts.STRONGHOLD_AUTON_LOW_BOULDERS] = SegmentMatch(number, teleop_high_goal_category, score_breakdown['teleopBouldersHigh'], teams)
#
#        result[cts.STRONGHOLD_AUTON_LOW_BOULDERS] = SegmentMatch(number, auton_low_goal_category, score_breakdown['autoBouldersLow'], teams)
#
#        result[cts.STRONGHOLD_AUTON_LOW_BOULDERS] = SegmentMatch(number, auton_high_goal_category, score_breakdown['autoBouldersHigh'], teams)
        return ut.get_segment_match_map(number, score_breakdown, teams, cts.STRONGHOLD_CATEGORIES)
        
