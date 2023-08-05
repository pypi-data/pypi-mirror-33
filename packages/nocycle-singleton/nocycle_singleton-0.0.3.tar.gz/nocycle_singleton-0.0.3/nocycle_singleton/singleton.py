#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
单例类
"""


class SingletonMeta(type):
    """
    单体类的元类，确保类的单例只初始化一次,
    """
    def __new__(mcs, name, bases, attr):
        """
        重新定义__init__函数
        """
        if "__init__" in attr:
            attr["__init__"] = mcs.init_wrapper(attr["__init__"])
        return type.__new__(mcs, name, bases, attr)

    @staticmethod
    def init_wrapper(init):
        """
        __init__的装饰器
        """
        setattr(init, "initial_class_set", set())

        def wrapper(self, *args, **kwargs):
            """
            包装之后的__init__, 对于每个子类，只执行一次
            """
            if not hasattr(init, "initial_class_set"):
                setattr(init, "initial_class_set", set())

            initial_class_set = getattr(init, "initial_class_set")
            current_class = self.__class__

            if current_class not in initial_class_set:
                initial_class_set.add(current_class)
                return init(self, *args, **kwargs)

        return wrapper


class Singleton(object):
    """
    单例类
    继承此类后，类都为Singleton
    """
    __metaclass__ = SingletonMeta
    _instance = None

    def __new__(cls, *args, **kargs):
        """
        真正的 "构造" 函数
        """
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kargs)
        else:
            # 继承此类的类也是Singleton
            if cls._instance.__class__ != cls:
                cls._instance = super(Singleton, cls).__new__(cls, *args, **kargs)

        return cls._instance
