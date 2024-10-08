from abc import ABC
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType


@dataclass
class Operator_:
    name: str
    symbol: str
    is_function: bool = False
    not_: bool = False
    two_values: bool = False


class Operations:
    class Operation(Enum):
        CONTAINS = Operator_('Contém subtexto', 'str.contains', is_function=True)
        NOT_CONTAINS = Operator_('Não contém subtexto', 'str.contains', is_function=True, not_=True)
        GREATER_THAN = Operator_('Maior que', '>')
        LESS_THAN = Operator_('Menor que', '<')
        EQUALS = Operator_('Igual a', '==')
        NOT_EQUALS = Operator_('Diferente de', '!=')
        BETWEEN = Operator_('Entre', 'between', is_function=True, two_values=True)

    by_type = MappingProxyType({
        'text': [
            Operation.CONTAINS,
            Operation.NOT_CONTAINS,
            Operation.EQUALS,
            Operation.NOT_EQUALS
        ],
        'number': [
            Operation.GREATER_THAN,
            Operation.LESS_THAN,
            Operation.EQUALS,
            Operation.NOT_EQUALS,
            Operation.BETWEEN
        ],
        'date': [
            Operation.GREATER_THAN,
            Operation.LESS_THAN,
            Operation.EQUALS,
            Operation.NOT_EQUALS,
            Operation.BETWEEN],
        'time': [
            Operation.GREATER_THAN,
            Operation.LESS_THAN,
            Operation.EQUALS,
            Operation.NOT_EQUALS,
            Operation.BETWEEN],
        'datetime': [
            Operation.GREATER_THAN,
            Operation.LESS_THAN,
            Operation.EQUALS,
            Operation.NOT_EQUALS,
            Operation.BETWEEN
        ],
        'checkbox': [
            Operation.EQUALS,
            Operation.NOT_EQUALS]
    })

    @staticmethod
    def by_name(name: str) -> Operation:
        op = next((op for op in Operations.Operation if op.value.name == name), None)
        if not op:
            raise ValueError(f'Operação não encontrada: {name}')
        return op
