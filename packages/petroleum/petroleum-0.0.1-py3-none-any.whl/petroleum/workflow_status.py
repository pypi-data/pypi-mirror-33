class WorkflowStatus:
    COMPLETED = 'COMPLETED'
    SUSPENDED = 'SUSPENDED'
    FAILED = 'FAILED'

    def __init__(self, status, outputs=None, exception=None):
        self.status = status
        self.outputs = outputs
        self.exception = exception

    def __repr__(self):
        return '<%s (%s)>' % (self.__class__.__name__, self.status)
