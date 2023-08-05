# -*- coding: utf-8 -*-

import logging

__all__ = ['LoggerMixin']


class LoggerMixin(object):
    """
    Mixin Class provides a :attr:`logger` (:class:`logging.Logger`)  property

    You can use it for **logger name as class name** ::

        class YourChildClass(YourParentClass, LoggerMixin):
            def your_method(self):
                self.logger.info('this is my logging text.')
    """

    @classmethod
    def get_logger(cls):
        """`logger` instance.

        :rtype: logging.Logger

        logger name format is `ModuleName.ClassName`
        """
        try:
            name = '{0.__module__:s}.{0.__qualname__:s}'.format(cls)
        except AttributeError:
            name = '{0.__module__:s}.{0.__name__:s}'.format(cls)
        return logging.getLogger(name)

    @property
    def logger(self):
        """`logger` instance.

        :rtype: logging.Logger

        logger name format is `ModuleName.ClassName`
        """
        return self.get_logger()
