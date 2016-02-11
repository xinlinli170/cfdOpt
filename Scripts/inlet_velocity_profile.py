from math import exp, tan

class InletVelocityProfile(object):
    """Storing the inlet velocity profile created by other classes.
    """

    def __init__(self):
        self.radius = []
        self.Va = []
        self.Vr = []
        self.Vt = []

    def print_profiles(self):
        print self.radius
        print self.Va
        print self.Vr
        print self.Vt
