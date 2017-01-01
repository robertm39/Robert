class Category:

    def __init__(self, stacking, score_req, match_phase, name):
        self.stacking = stacking
        self.score_req = score_req
        self.match_phase = match_phase
        self.name = name

    def __eq__ (self, other):
        return self.stacking == other.stacking and self.score_req == other.score_req and self.match_phase == other.match_phase and self.name == other.name
    
    def __neq__ (self, other):
        return not self == other

    def __hash__ (self):
        return hash((self.stacking, self.score_req, self.match_phase, self.name))

    def __repr__(self):
        stack_string = ""
        
        if(self.stacking):
            stack_string = "Stacking"
        else:
            stack_string = "Non-Stacking"

        return "(" + self.name + " " + stack_string + " " + self.score_req.name + " " + self.match_phase.name + ")"

    def __str__(self):
        return self.__repr__()
