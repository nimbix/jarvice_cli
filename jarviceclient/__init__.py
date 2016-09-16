import logging

__version__ = '0.9.4'
__all__ = ['utils', 'JarviceAPI']

FORMAT =\
  "[%(levelname)s] %(module)s.%(filename)s.%(funcName)s %(lineno)d %(message)s"
logger = logging.getLogger(__name__)
logger.debug('import %s' % __name__)
logging.basicConfig(level=logging.CRITICAL, format=FORMAT)
