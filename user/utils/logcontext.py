import sys
from contextlib import ContextDecorator
from functools import wraps, partial
from typing import Any, Union

from loguru import logger
import inspect
from copy import deepcopy

LogC = Union[dict[str, Any], None]


class Context:
    def __init__(self, add_tags: Union[list[str], None], logc: LogC = None):
        if logc is None:
            logc = dict[str, Any]()
            logc['tags'] = []

        self.logcontext = deepcopy(logc)
        self.logcontext['tags'] += add_tags
        # self.logcontext.update({'tags': add_tags})

        self.__internal_logcontext = deepcopy(self.logcontext)
        self.__internal_logcontext['tags'].append('context_managing')

    def __enter__(self) -> LogC:
        logger.opt(depth=1).debug('Entering context {tags}', **self.__internal_logcontext)
        return self.logcontext

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.opt(depth=1).debug('Exiting context {tags}', **self.__internal_logcontext)

    @staticmethod
    def decorate_function(add_extra: list[str]):
        def contextualizing(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                logger.debug(f'args: {args}')
                logger.debug(f'kwargs: {kwargs}')
                if 'logc' not in kwargs:
                    raise ValueError(f'`logc=...` not in `{func.__name__}` kwargs. '
                                     f'always use param `logc=...` in function calls')
                if 'tags' not in kwargs['logc']:
                    logger.opt(depth=1).info(f'creating the tags context from scratch')
                    kwargs['logc']['tags'] = list[str]()
                kwargs['logc'] = deepcopy(kwargs['logc'])
                kwargs['logc']['tags'] += add_extra
                func(*args, **kwargs)

            return wrapper

        return contextualizing


@Context.decorate_function(add_extra=['3'])
def funcao1(logc: dict[str, Any]):
    logger.opt(depth=0).debug('tags: {tags}', **logc)  # usar locals() para não precisar desse parametro **logc


@Context.decorate_function(add_extra=['4'])
def funcao2(logc: dict[str, Any]):
    logger.opt(depth=0).debug('tags: {tags}', **logc)
    with Context(logc=logc, add_tags=['5']) as logc:
        logger.opt(depth=0).debug('tags: {tags}', **logc)
        funcao1(logc=logc)


if __name__ == '__main__':
    with Context(add_tags=['1']) as logc:
        logger.debug('tags: {tags}', **logc)
        funcao1(logc=logc)
        funcao2(logc=logc)

        with Context(logc=logc, add_tags=['2']) as logc:
            logger.debug('tags: {tags}', **logc)
            funcao1(logc=logc)
            funcao2(logc=logc)

# bug logger.debug não funciona com string com caracteres "{" ou "}", ou seja, não dá para loggar um dicionário
