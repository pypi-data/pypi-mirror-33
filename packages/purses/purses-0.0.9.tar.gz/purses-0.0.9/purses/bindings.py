class binding_(object):
    """Register key bindings with the object binding."""

    def __init__(self):
        self.bindings = {}

    def __call__(self, key):
        def register(func):
            def decorator(model, nav, io, *args, **kwargs):
                res = func(model, nav, io, *args, **kwargs)
                return res

            self.bindings[key] = decorator
            return decorator

        return register


# this object works as a decorator for registering key bindings
binding = binding_()
