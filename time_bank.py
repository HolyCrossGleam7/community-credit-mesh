class TimeBank:
    def __init__(self):
        self.hours_worked = 0

    def add_hours(self, hours):
        if hours > 0:
            self.hours_worked += hours
        else:
            print("Invalid hours input. Must be positive.")

    def subtract_hours(self, hours):
        if 0 < hours <= self.hours_worked:
            self.hours_worked -= hours
        else:
            print("Invalid hours input. Must not exceed hours worked.")

    def get_hours(self):
        return self.hours_worked

    def __str__(self):
        return f'Total hours worked: {self.hours_worked}'
