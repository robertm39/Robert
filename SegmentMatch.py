class SegmentMatch:

    def __init__(self, number, category, amount, teams):
        self.number = number
        self.category = category
        self.amount = amount
        self.teams = teams

    def __eq__(self, other):
        return self.number == other.number and self.category == other.category and self.amount == other.amount and self.teams == other.teams

    def __neq__(self, other):
        return not self == other

    def __repr__(self):
        return "(#" + self.number.__repr__() + " " + self.teams.__repr__() + " " + self.category.__repr__() + " " + self.amount.__repr__() + ")"

    def __str__(self):
        return self.__repr__()
