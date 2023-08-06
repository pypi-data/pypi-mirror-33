from petroleum.conditional_task import ConditionalTask
from petroleum.task import Task


class ExclusiveChoice(Task):
    def __init__(self, name, *args, **kwargs):
        self.conditional_tasks = []
        super().__init__(name, *args, **kwargs)

    def get_next_task(self, inputs):
        for conditional_task in self.conditional_tasks:
            result = conditional_task.condition(inputs)
            if not isinstance(result, bool):
                raise Exception('Condition %s did not return bool' %
                                conditional_task.condition)
            if result is True:
                return conditional_task.task
        return next(conditional_task.task for conditional_task in
                    self.conditional_tasks if conditional_task.default is True)

    def connect(self, task, condition):
        conditional_task = ConditionalTask(task=task, condition=condition)
        if len(self.conditional_tasks) == 0:
            conditional_task.default = True
        self.conditional_tasks.append(conditional_task)

    def run(self, inputs):
        return inputs
