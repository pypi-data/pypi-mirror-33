import inspect
import logging
from threading import RLock

from scopeton import compat
from scopeton.objects import Bean
from scopeton.scopeTools import getBeanName, callMethodByName, ScopetonException


class Scope(object):
    '''this is servicelocator pattern implementation'''
    def __init__(self, lock=False, initMethod="postConstruct", destroyMethod="preDestroy", parent=None):
        self._singletons = {}  # type: dict[str, Bean]
        self._beans = {}       # type: dict[str, Bean]
        self.lock = lock       # type: RLock
        self.initMethod = initMethod
        self.destroyMethod = destroyMethod
        self.parent = parent    #type: Scope

    def getInstance(self, name):
        if self.lock:
            self.lock.acquire()
        try:
            return self._getInstance(getBeanName(name))
        finally:
            if self.lock: self.lock.release()

    def _getInstance(self, name):
        name = getBeanName(name)
        if name in self._singletons:
            return self._singletons[name]

        if name not in self._beans:
            raise Exception("Error, no such bean:" + str(name))

        bean = self._beans[name]
        if len(compat.getMethodSignature(bean.cls.__init__).args) == 2:
            instance = bean.cls(self)
        else:
            instance = bean.cls()

        if bean.singleton:
            self._singletons[name] = instance
        return instance

    def registerBean(self, *args):
        if self.lock:
            self.lock.acquire()
        try:
            for bean in args:
                self._registerBean(bean)
        finally:
            if self.lock: self.lock.release()

    def _registerBean(self, bean):
        """
        :type bean: Bean
        """
        name = getBeanName(bean)
        logging.debug("Registering:" + name)
        if name in self._beans:
            raise ScopetonException("Error, bean with name {} already registered".format(name))
        self._beans[getBeanName(bean)] = bean

    def runServices(self):
        for k in self._beans:
            bean = self._beans[k]
            if bean.service:
                callMethodByName(self.getInstance(bean), self.initMethod)
