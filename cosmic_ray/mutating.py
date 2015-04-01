import ast
import logging
import sys
import types
from collections import namedtuple


log = logging.getLogger()


MutationRecord = namedtuple('MutationRecord', ['module_name',
                                               'module_file',
                                               'operator',
                                               'activation_record',
                                               'mutant'])


def create_mutants(modules, operators):
    """Mutate `modules` with `operators`.

    Returns an iterable of `MutationRecord`s, one for each application
    of an operator to a location in a module.

    """
    for module in modules:
        with open(module.__file__, 'rt', encoding='utf-8') as f:
            log.info('reading module {} from {}'.format(
                module.__name__, module.__file__))
            source = f.read()

        pristine_ast = ast.parse(source, module.__file__, 'exec')

        for operator in operators:
            for activation_record, mutant in operator.bombard(pristine_ast):
                yield MutationRecord(module_name=module.__name__,
                                     module_file=module.__file__,
                                     operator=operator,
                                     activation_record=activation_record,
                                     mutant=mutant)


class TimeoutException(Exception):
    pass


def raise_timeout_exception():
    raise TimeoutException()


def run_with_mutant(func, mutation_record):
    """Install the mutation record and run func, returning its result.
    """
    module_name, module_file, _, _, mutant = mutation_record
    new_mod = types.ModuleType(module_name)
    code = compile(mutant, module_file, 'exec')
    sys.modules[module_name] = new_mod
    exec(code,  new_mod.__dict__)
    return func()
