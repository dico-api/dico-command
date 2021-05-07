class Command:
    def __init__(self,
                 func,
                 name: str,
                 args: iter = None,
                 checks: iter = None):
        self.func = func
        self.name = name
        self.args = args or []
        self.checks = checks or []

    def invoke(self, *args, **kwargs):
        return self.func(*args, **kwargs)
