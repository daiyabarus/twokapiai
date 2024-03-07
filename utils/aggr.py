class Aggr:
    def __init__(self, previous_value, current_value):
        self.previous_value = previous_value
        self.current_value = current_value

    @property
    def delta(self):
        return round(self.current_value - self.previous_value, 2)

    @property
    def delta_percent(self):
        if self.previous_value == 0:
            if self.current_value != 0:
                return float("inf")
            else:
                return 0
        return abs(round((self.delta / self.previous_value) * 100, 2))

    @property
    def flag(self):
        if self.delta >= 0 and self.delta_percent > 10:
            return "Improve"
        elif self.delta < 0 and self.delta_percent > 10:
            return "Degrade"
        else:
            return "Maintain"

    @property
    def flagdrop(self):
        if self.delta <= 0 and self.delta_percent > 10:
            return "Improve"
        elif self.delta > 0 and self.delta_percent > 10:
            return "Degrade"
        else:
            return "Maintain"
