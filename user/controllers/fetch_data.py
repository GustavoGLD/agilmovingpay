import datetime
import decimal

import pandas as pd
import sqlalchemy
import streamlit as st
from loguru import logger
from sqlalchemy import Engine
from streamlit.elements.lib.column_types import ColumnConfig

from models.Borg import *


@st.cache_data
def get_df(_engine: Engine, table: str, schema: str = None) -> pd.DataFrame:
    """
    Pega os dados da tabela e retorna um dataframe
    :return: dataframe
    """
    with _engine.connect() as conn:
        insp = sqlalchemy.inspect(_engine)
        try:
            df = pd.read_sql_table(table, conn, schema=schema, dtype_backend='pyarrow')
        except Exception as e:
            error_text = str(e)
            if st.session_state['url'] in error_text:
                error_text = error_text.replace(st.session_state['url'], 'DATABASE_URL')
            logger.warning(f'Não foi possível obter os dados da tabela {table} com o método read_sql_table: {error_text}')
            logger.debug(f"SELECT * FROM {schema}.{table}")
            df = pd.read_sql(f"SELECT * FROM {schema}.{table}", conn)
    logger.info(f'Obtendo dados da tabela {table}')
    return df


@st.cache_data
def fetch_data(_engine: Engine, table: str, schema: str = None, _borg=Borg()) -> tuple[pd.DataFrame, dict[str, Any], dict]:
    """
    Pega os dados da tabela e retorna um dataframe e um dicionário de configuração de colunas para o data editor
    :return: dataframe e dicionário de configuração de colunas
    """

    insp = sqlalchemy.inspect(_engine)
    df = get_df(_engine, table, schema)
    columns_table = insp.get_columns(table, schema=schema)
    logger.info(f'Obtendo dados da tabela {table}')

    column_config = {}
    for col in columns_table:
        equivalent_types = {
            str: st.column_config.TextColumn,
            float: st.column_config.NumberColumn,
            int: st.column_config.NumberColumn,
            bool: st.column_config.CheckboxColumn,
            datetime.datetime: st.column_config.DatetimeColumn,
            datetime.date: st.column_config.DateColumn,
            datetime.time: st.column_config.TimeColumn,
            decimal.Decimal: st.column_config.NumberColumn
        }
        others_equivalent_types = {
            'MONEY': (st.column_config.NumberColumn, {'format': 'R$ %.2f'}),
            'SMALLMONEY': (st.column_config.NumberColumn, {'format': 'R$ %.2f'}),
            'SMALLDATETIME': (st.column_config.DateColumn, {}),
        }

        try:
            if col['type'].python_type == datetime.datetime \
                    and col['default'] == 'current_timestamp()':
                col['default'] = datetime.datetime.now()
        except Exception as e:
            pass

        try:
            if 'autoincrement' in col and col['autoincrement']:
                autoincr = _borg.autoincr[_borg.tablename] or []
                autoincr.append(col['name'])
                _borg.autoincr[_borg.tablename] = autoincr

                column_config[col['name']] = st.column_config.NumberColumn(
                    label=f"{col['name']} [AUTODEFINIDO]",
                    required=not col['nullable'],
                    default=None,
                    disabled=True,
                    help=f"Valor a definir no banco de dados",
                )
                logger.info(f'autoincr: {autoincr}')
            elif str(col['type']).upper() in list(others_equivalent_types.keys()):
                column_config[col['name']] = others_equivalent_types[str(col['type']).upper()][0](
                    label=f"{col['name']}",
                    required=not col['nullable'],
                    default=col['default'],
                    help=f"{col['type']}",
                    **others_equivalent_types[str(col['type']).upper()][1]
                )
            elif col['type'].python_type in list(equivalent_types.keys()):
                column_config[col['name']] = equivalent_types[col['type'].python_type](
                    label=f"{col['name']}",
                    required=not col['nullable'],
                    default=col['default'],
                    help=f"{col['type']}",
                    **{'max_chars': col['type'].length} if col['type'].python_type == str
                    and 'length' in col['type'].__dict__ and type(col['type'].length) == int else {},
                    **{'step': 1} if col['type'].python_type == int else {},
                )
            elif col['type'].python_type in [bytes, bytearray, datetime.timedelta]:
                raise NotImplementedError(f'Não implementado para {col["type"].python_type.__name__}')
            else:
                raise NotImplementedError(f'Tipo desconhecido ainda não implementado')

        except NotImplementedError as e:
            error_text = str(e)
            if st.session_state['url'] in error_text:
                error_text = error_text.replace(st.session_state['url'], 'DATABASE_URL')
            logger.warning(f'Não foi possível obter o tipo da coluna {col["name"]} da tabela {table}: {error_text}')
            st.warning(f'🤔❓ Tipo SQL "{col["type"]}" desconhecido. a coluna "{col["name"]}" será tratada como texto')
            column_config[col['name']] = st.column_config.TextColumn(
                label=f"{col['name']}",
                required=not col['nullable'],
                help=f"unknown type"
            )

    #logger.debug(f'column_config: {column_config}\ncolumns_table: {columns_table}')
    return df, column_config, columns_table
