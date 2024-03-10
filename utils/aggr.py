class Aggr:
    def __init__(self, pre, post):
        self.pre = pre
        self.post = post

    @property
    def delta(self):
        return round(self.post - self.pre, 2)

    @property
    def delta_percent(self):
        if self.pre == 0:
            if self.post != 0:
                return float("inf")
            else:
                return 0
        return abs(round((self.delta / self.pre) * 100, 2))

    @property
    def flag(self):
        if self.delta > 0 and self.delta_percent > 5:
            return "Improve"
        elif self.delta < 0 and self.delta_percent > 5:
            return "Degrade"
        else:
            return "Maintain"

    @property
    def flag10(self):
        if self.delta > 0 and self.delta_percent > 10:
            return "Increased"
        elif self.delta < 0 and self.delta_percent > 10:
            return "Decreased"
        else:
            return "Stable"

    @property
    def flagdrop(self):
        if self.delta < 0 and self.delta_percent > 5:
            return "Improve"
        elif self.delta > 0 and self.delta_percent > 5:
            return "Degrade"
        else:
            return "Maintain"

    @property
    def flagdrop10(self):
        if self.delta < 0 and self.delta_percent > 10:
            return "Improve"
        elif self.delta > 0 and self.delta_percent > 10:
            return "Degrade"
        else:
            return "Maintain"

    @property
    def _flagdrop10(self):
        if self.delta > 0 and self.delta_percent > 10:
            return "Improve"
        elif self.delta < 0 and self.delta_percent > 10:
            return "Degrade"
        else:
            return "Maintain"

    @property
    def _flagtarget(self):
        if self.post >= self.pre:
            return "Pass"
        else:
            return "Fail"

    @property
    def _flagtargetdrop(self):
        if self.post <= self.pre:
            return "Pass"
        else:
            return "Fail"
