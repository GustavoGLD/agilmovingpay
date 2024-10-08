import copy
import re
from typing import Any

import pandas as pd
import streamlit as st
from loguru import logger

from models import QueryParameterLayout
from models.Operation import Operations
from models.QueryParameterLayout import define_query_parameter_layout
from models.SessionState import SessionState


def make_condition(table: pd.DataFrame, query_layout: QueryParameterLayout) -> pd.DataFrame:
    value = query_layout.slct_value
    column = table[query_layout.slct_col]
    operation_name = query_layout.slct_op

    if not value or column.empty or not operation_name:
        return table

    operation = Operations.by_name(operation_name)

    query = ''
    if operation.value.not_:
        query += 'not '

    if operation.value.is_function and not operation.value.two_values \
            and operation.value.symbol == Operations.Operation.CONTAINS.value.symbol:
        ignore = re.IGNORECASE
        query += f'@column.{operation.value.symbol}(@value, flags=@ignore)'
    elif operation.value.is_function and not operation.value.two_values:
        query += f'@column.{operation.value.symbol}(@value)'
    elif operation.value.is_function and operation.value.two_values:
        query += f'@column.{operation.value.symbol}(@value[0], @value[1])'
    elif operation.value.is_function and operation.value.two_values:
        query += f'@column.{operation.value.symbol}(@value[0], @value[1])'
    elif not operation.value.is_function and not operation.value.two_values:
        query += f'@column {operation.value.symbol} @value'
    else:
        raise ValueError(f'Operação {operation.value.name} não implementada')
    return table.query(query)


class MyQuery:
    @staticmethod
    def layout(col_name: str, col: dict, layout: QueryParameterLayout) -> QueryParameterLayout:
        layout.slct_col = col_name
        layout.column.write(' ')
        layout.column.markdown(f"""{col_name}""")
        layout.slct_type = col['type_config']['type']
        return layout

    @staticmethod
    def layout_multiselect(stt=SessionState()) -> list[str]:
        return st.multiselect('🔍 Colunas de Pesquisa', stt.columns_config[stt.tablename.value].keys())

    @staticmethod
    def run(stt=SessionState()) -> list[QueryParameterLayout]:
        search_cols = MyQuery.layout_multiselect()
        query_layouts = list[QueryParameterLayout]()
        component = define_query_parameter_layout()

        stt.values[stt.tablename.value] = dict[str, tuple[str, Any]]()
        for col_name, col in [(s, stt.columns_config[stt.tablename.value][s]) for s in search_cols]:
            a: QueryParameterLayout = MyQuery.layout(col_name, col, component(col_name))
            query_layouts.append(a)
            a.run()
            stt.values[stt.tablename.value][col_name] = (a.slct_op, a.slct_value)

        if (
                not stt.last_value.exists(stt.tablename.value)
                or stt.last_value[stt.tablename.value] != stt.values[stt.tablename.value]
        ):
            stt.last_value[stt.tablename.value] = copy.deepcopy(stt.values[stt.tablename.value])
            stt.original_df[stt.tablename.value] = stt.edited_df[stt.tablename.value].copy()
            stt.original2_df[stt.tablename.value] = stt.edited_df[stt.tablename.value].copy()
            #logger.critical(f'Valores de pesquisa alterados {stt.values[stt.tablename.value]}')


        stt.query_layouts[stt.tablename.value] = query_layouts
        return query_layouts

    @staticmethod
    def get_result(df_rslt: pd.DataFrame, stt=SessionState()) -> pd.DataFrame:
        for ql in stt.query_layouts[stt.tablename.value]:
            df_rslt = make_condition(df_rslt, ql)
        return df_rslt

    def __init__(self, stt=SessionState()):
        self.layouts = MyQuery.run()
        self.df_rslt = MyQuery.get_result(stt.table_df[stt.tablename.value], stt)

    @staticmethod
    def manage_edited_rows(df_search_res: pd.DataFrame, edited_rows: dict, stt=SessionState()):
        # edited_rows retorna um dicionário com índices diferentes dos índices do dataframe
        # ex.: índices [2, 4, 7] viram [0, 1, 2]
        # então é necessário fazer essa conversão, primeiro

        # salva os índices antigos
        old_index = df_search_res.index

        # reseta os índices
        df_search_res.index = range(len(df_search_res))

        # itera sobre os índices e colunas editadas salvando no dataframe resultando da query
        for index, row in edited_rows.items():
            for col, value in row.items():
                df_search_res.at[index, col] = value

        # reseta os índices resetados para os antigos
        df_search_res.index = old_index

        edited_df = stt.edited_df[stt.tablename.value]
        # itera sobre todos índices e colunas do dataframe resultado da query, salvando no dataframe original
        for index, row in df_search_res.iterrows():
            for col, value in row.items():
                # logger.debug(f'df_search_res index: {index}, col: {col}, value: {value}')
                edited_df.at[index, col] = value

        stt.edited_df[stt.tablename.value] = edited_df.copy()

    @staticmethod
    def manage_deleted_rows(df_search_res: pd.DataFrame, deleted_rows: list, stt=SessionState()):
        # deleted_rows retorna uma lista de índices diferentes dos índices do dataframe
        # ex.: índices [2, 4, 7] viram [0, 1, 2]
        # então é necessário fazer essa conversão, primeiro
        deleted_rows = df_search_res.index[deleted_rows].tolist()
        # logger.info(f'deleted_rows: {deleted_rows}')

        # itera sobre os índices deletados e deleta do dataframe original
        edited_df = stt.edited_df[stt.tablename.value]
        edited_df.drop(deleted_rows, inplace=True)
        stt.edited_df[stt.tablename.value] = edited_df.copy()

    @staticmethod
    def on_change_query(stt=SessionState()):
        df = stt.original2_df[stt.tablename.value]
        df_search_res: pd.DataFrame = MyQuery.get_result(df, stt)
        MyQuery.manage_edited_rows(
            df_search_res.copy(),
            stt.table_changes[stt.tablename.value]['edited_rows']
        )
        MyQuery.manage_deleted_rows(
            df_search_res.copy(),
            stt.table_changes[stt.tablename.value]['deleted_rows']
        )
        stt.original_df[stt.tablename.value] = stt.edited_df[stt.tablename.value].copy()
