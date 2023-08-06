class ConditionalTask:
    def __init__(self, task, condition, default=False):
        self.task = task
        self.condition = condition
        self.default = default
