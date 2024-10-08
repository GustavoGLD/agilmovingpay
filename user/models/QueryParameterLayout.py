import copy
from abc import ABC, abstractmethod
import streamlit as st
from typing import Any, Type

import pandas as pd
from dateutil.parser import parse
from loguru import logger
from streamlit.delta_generator import DeltaGenerator

from models.SessionState import SessionState
from models.Operation import Operations


def define_query_parameter_layout() -> Type["QueryParameterLayout"]:
    class Layout(ABC):
        components = []

        def run(self): ...

    class Base(ABC):
        @abstractmethod
        def run(self, layout: "QueryParameterLayout"):
            ...

        @classmethod
        def __init_subclass__(cls, **kwargs):
            if 'layout' not in kwargs:
                raise ValueError(f'`layout` not in `{cls.__name__}` kwargs. ')
            if not issubclass(kwargs['layout'], Layout):
                raise TypeError(f'{kwargs["layout"]=} must be a subclass of `Layout`')
            kwargs['layout'].components.append(cls)

    class QueryParameterLayout(Layout):
        def __init__(self, key: str, container=st.container(border=True)):
            self.slct_col = None
            self.slct_op = None
            self.slct_type = None
            self.slct_value = None

            self.key = key

            self.left, self.center, self.right = container.columns(3)
            self.column: DeltaGenerator = self.left.container(border=True)
            self.operation: DeltaGenerator = self.center.container()
            self.value: DeltaGenerator = self.right.container()

        def run(self):
            for component in self.components:
                component().run(self)

    class SelectOperation(Base, layout=QueryParameterLayout):
        def run(self, layout: QueryParameterLayout):
            if not layout.slct_type:
                return None

            assert layout.slct_type in Operations.by_type.keys(), \
                f'Tipo {layout.slct_type} não achado em {Operations.by_type.keys()}'

            layout.slct_op = layout.operation.selectbox(
                'Selecione a operação',
                [op.value.name for op in Operations.by_type[layout.slct_type]],
                key=f'{layout.key}_slct_op'
            )

    class SelectValue(Base, layout=QueryParameterLayout):
        @staticmethod
        def parse_value(layout: QueryParameterLayout, value: str) -> Any:
            if not value:
                return None
            if layout.slct_type == 'datetime':
                value = parse(value)
            elif layout.slct_type == 'date':
                value = parse(value).date()
            elif layout.slct_type == 'time':
                value = parse(value).time()
            elif layout.slct_type == 'number':
                value = float(value)
            if not layout.slct_op:
                value = None
            return value

        def run(self, layout: QueryParameterLayout, stt=SessionState()):
            if not layout.slct_type:
                return None

            column_config = copy.deepcopy(stt.columns_config[stt.tablename.value][layout.slct_col])

            label = 'Valor_de_pesquisa'
            column_config['label'] = label
            column_config['required'] = True

            two_values = Operations.by_name(layout.slct_op).value.two_values
            data = pd.DataFrame({label: [None, None]}) if two_values else pd.DataFrame({label: [None]})

            slct_value = layout.value.data_editor(
                data=data,
                column_config={label: column_config},
                hide_index=True,
                use_container_width=True,
                key=f'{layout.key}_slct_value',
            )
            slct_value = pd.DataFrame(slct_value).to_dict('list')[label]

            if not slct_value:
                layout.slct_value = None
            elif not two_values:
                layout.slct_value = SelectValue.parse_value(layout, slct_value[0])
            elif two_values and not slct_value[0] or not slct_value[1]:
                layout.two_values = pd.DataFrame({label: [None, None]})
            elif two_values:
                value1 = SelectValue.parse_value(layout, slct_value[0])
                value2 = SelectValue.parse_value(layout, slct_value[1])
                layout.slct_value = [value1, value2]
                layout.slct_value.sort()

    return QueryParameterLayout
