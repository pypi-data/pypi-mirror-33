from scopeton.scopeTools import getBeanName


class Bean(object):
    name = ""
    cls = None  # type: type
    lazy = False
    singleton = True

    def __init__(self, cls, name=None, lazy = False, singleton=True, service = True):
        self.cls = cls
        self.name = getBeanName(name) if name else getBeanName(cls)
        self.lazy = lazy
        self.singleton = singleton
        self.service = service
        if not singleton and service:
            raise Exception("Error, cannot initialize service as non singleton")



