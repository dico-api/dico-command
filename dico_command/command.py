from .utils import read_function


class Command:
    def __init__(self,
                 func,
                 name: str,
                 checks: iter = None):
        self.func = func
        self.name = name
        self.checks = checks or []

        self.args_data = read_function(self.func)

    def invoke(self, ctx, *args, **kwargs):
        return self.func(ctx, *args, **kwargs)
