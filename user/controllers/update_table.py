import copy
import datetime
import decimal
import io
import re
import typing
import unittest
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from functools import partial
from types import MappingProxyType
from typing import Any, Type, Union, Callable, TypeVar, Generic, Literal, NewType
import inspect

import sqlalchemy
import streamlit as st
import pandas as pd
from dateutil.parser import parse
from loguru import logger


from pathlib import Path
import sys

from pypika import Query, Table
from pypika.queries import QueryBuilder
from sqlalchemy import Connection, text
from sqlalchemy.exc import CompileError
from streamlit.delta_generator import DeltaGenerator
from streamlit_modal import Modal

from controllers.myquery import make_condition, MyQuery
from models.Operation import Operations
from models.SessionState import SessionState
from utils import Context, LogC

sys.path.append(str(Path(__file__).resolve().parent.parent))

from controllers import init_connection, fetch_data
from models import Borg, BorgObj, BorgName, Default, QueryParameterLayout
from models.QueryParameterLayout import define_query_parameter_layout


SCHEMA = st.secrets['database']['schema']

@Context.decorate_function(add_extra=['fetch_table_data'])
def fetch_table_data(tablename: str, logc: LogC, stt=SessionState()):
    df, column_config, columns_table = fetch_data(init_connection(), tablename, SCHEMA, stt)

    stt.edited_df[tablename] = Default(df)
    stt.table_df[tablename] = Default(df)
    stt.columns_config[tablename] = Default(column_config)
    stt.columns_table[tablename] = Default(columns_table)

    #logger.debug(f'\ndf:\n{stt.table_df[tablename].to_markdown()}', **logc)
    #logger.debug(f'\ncolumn_config:\n{pd.DataFrame(stt.columns_config[tablename]).to_markdown().replace(r"{", r"[").replace(r"}", r"]")}', **logc)
    #logger.debug(f'\ncolumns_table:\n{pd.DataFrame(stt.columns_table[tablename]).to_markdown().replace(r"{", r"[").replace(r"}", r"]")}', **logc)


class TableEditor:
    @staticmethod
    def table_editor(table: pd.DataFrame, column_config: dict, container=st) -> pd.DataFrame:

        return container.data_editor(table, column_config=column_config, use_container_width=True, num_rows="dynamic")

    @staticmethod
    def render(stt=SessionState(), container=st):
        column_config = stt.columns_config[stt.tablename.value]
        df = TableEditor.table_editor(stt.original_df[stt.tablename.value], column_config, container=container)
        stt.edited_df[stt.tablename.value] = df.copy()
        stt.original2_df[stt.tablename.value] = df.copy()


class TableEditorQuery:
    @staticmethod
    def table_editor_with_query(table: pd.DataFrame, column_config: dict, key: str, on_change, container=st) -> pd.DataFrame:
        return container.data_editor(
            table,
            column_config=column_config,
            use_container_width=True,
            num_rows="dynamic",
            key=key,
            hide_index=True,
            on_change=on_change,
        )

    @staticmethod
    def render(stt=SessionState(), container=st):
        df = TableEditorQuery.table_editor_with_query(
            MyQuery.get_result(stt.original2_df[stt.tablename.value]),
            stt.columns_config[stt.tablename.value],
            key=f'{stt.tablename.value}_table_changes',
            on_change=MyQuery.on_change_query,
            container=container
        )
        # borg.edited_df[borg.tablename] = df.copy()
        # borg.original2_df[borg.tablename] = df.copy()
        # borg.original_df[borg.tablename] = borg.edited_df[borg.tablename].copy()
        stt.original_df[stt.tablename.value] = stt.edited_df[stt.tablename.value].copy()


def execute_query(query: QueryBuilder, conn: Connection):
    logger.debug(f'Query:\n{query.get_sql()}')
    # try:
    conn.execute(text(query.get_sql()))
    conn.commit()


def substituir_aspas(texto):
    if isinstance(texto, str):  # Verifica se é uma 'string'
        logger.debug(f'texto: {texto}')
        return texto.replace("'", r"''")
    else:
        return texto


class SaveBtt:

    @staticmethod
    def save(stt=SessionState()):
        with init_connection().connect() as conn:
            edited_df: pd.DataFrame = stt.edited_df[stt.tablename.value].copy()
            if stt.autoincr.exists(stt.tablename.value):
                edited_df = edited_df.drop(stt.autoincr[stt.tablename.value], axis=1)
            edited_df.apply(lambda x: x.map(substituir_aspas) if x.dtype == 'O' else x)
            _table = Table(stt.tablename.value, schema=SCHEMA)
            execute_query(Query.from_(_table).delete(), conn)
            execute_query(_table.insert(*edited_df.to_dict("split")['data']), conn)
            conn.commit()

            stt.table_df[stt.tablename.value] = stt.edited_df[stt.tablename.value].copy()
            stt.original_df[stt.tablename.value] = stt.edited_df[stt.tablename.value].copy()
            stt.original2_df[stt.tablename.value] = stt.edited_df[stt.tablename.value].copy()

    @staticmethod
    def render(container=st, stt=SessionState()):
        stt.savable[stt.tablename.value] = not stt.table_df[stt.tablename.value].equals(
            stt.edited_df[stt.tablename.value]
        )

        if stt.saving.exists(stt.tablename.value) and stt.saving[stt.tablename.value]:
            stt.savable[stt.tablename.value] = False

        if container.button('💾 Salvar Alterações', use_container_width=True):
            SaveBtt.save()


towrite = io.BytesIO()
export_fmts = {
    'csv': lambda df: df.to_csv().encode('utf-8'),
    'xml': lambda df: df.to_xml().encode('utf-8'),
    'html': lambda df: df.to_html().encode('utf-8'),
    #'json': lambda df: df.to_json().encode('utf-8'),
    #'xlsx': lambda df: (df.to_excel(towrite), towrite.getvalue())[1],
    #'parquet': lambda df: df.to_parquet(engine='pyarrow')
}


def converter(tablename: str, fmt: str) -> bytes:
    with init_connection().connect() as conn:
        try:
            df = pd.read_sql_table(tablename, conn, schema=SCHEMA, dtype_backend='pyarrow')
        except Exception:
            table = sqlalchemy.Table(tablename, sqlalchemy.MetaData(schema=SCHEMA), autoload_with=conn)
            df = pd.read_sql(table.select(), conn)

        towrite = io.BytesIO()

        return export_fmts[fmt](df)


def update_table(tablename: str):
    with Context(add_tags=['global']) as logc:
        stt = SessionState()
        stt.tablename = tablename

        fetch_table_data(tablename, logc=logc)

        tab1, tab2, tab3 = st.tabs(["📄 Editar/Consultar ", "📁 Exportar", "💽 SQL"])

        with tab1:
            query = MyQuery(stt)

            if stt.values[tablename] == {}:
                TableEditor.render()
            else:
                TableEditorQuery.render()

            SaveBtt.render()

        with tab2:
            style = "<style>h3 {text-align: center;}</style>"
            st.markdown(style, unsafe_allow_html=True)
            st.columns([1, 5, 1])[1].subheader(f':blue[↓] :blue[Exportar] :orange[{tablename.upper()}] :blue[↓]')

            cols = zip(st.columns(len(export_fmts.keys())), export_fmts.keys())

            def download_button(fmt: str):
                st.download_button(
                    f"Download ***{fmt.upper()}***",
                    converter(tablename, fmt),
                    f"{tablename}.{fmt}",
                    f"text/{fmt}",
                    key=f'download-{fmt}',
                    use_container_width=True
                )

            for col, fmt in cols:
                if col.button(fmt, use_container_width=True):
                    download_button(fmt)

            st.divider()
            st.markdown('⚠️ A exportação para :green[**XLSX**] pode :red[**limitar**] a quantidade de linhas e colunas exportadas.')
            st.markdown('💾 :red[**Salve**] as alterações para exportar os dados :green[**atualizados**].')
            st.markdown('⏳ Pode levar alguns segundos...')

        try:
            from sqlalchemy.schema import CreateTable
            from sqlalchemy.dialects import mysql
            with init_connection().connect() as conn:
                table = sqlalchemy.Table(tablename, sqlalchemy.MetaData(schema=SCHEMA), autoload_with=conn)
                a = str(CreateTable(table).compile(dialect=mysql.dialect()))
        except CompileError as e:
            with tab3:
                st.error(f'😔 Essa tabela contém tipos que o SQLAlchemy não consegue compilar: \n{str(e).split(" ")[-1]}')
        else:
            with tab3:
                from sqlalchemy.schema import CreateTable
                from sqlalchemy.dialects import mysql
                with init_connection().connect() as conn:
                    table = sqlalchemy.Table(tablename, sqlalchemy.MetaData(schema=SCHEMA), autoload_with=conn)
                    a = str(CreateTable(table).compile(dialect=mysql.dialect()))

                    def insert_script() -> str:
                        b = sqlalchemy.insert(table).values(
                            pd.read_sql_table(tablename, conn, schema=SCHEMA).to_dict('records'))
                        return str(b.compile(dialect=mysql.dialect(), compile_kwargs={"literal_binds": True}))

                    st.subheader(':blue[↓ Scripts] :orange[SQL] :blue[↓]')
                    b_create, b_insert = st.columns(2)
                    if b_create.button('CREATE', use_container_width=True):
                        st.download_button(
                            "Download ***CREATE*** script",
                            a,
                            f"{tablename}-create.sql",
                            "text/sql",
                            key=f'download-create-sql',
                            use_container_width=True
                        )

                    if b_insert.button('INSERT', use_container_width=True):
                        st.download_button(
                            "Download ***INSERT*** script",
                            insert_script(),
                            f"{tablename}-insert.sql",
                            "text/sql",
                            key=f'download-sql',
                            use_container_width=True
                        )

                st.divider()
                st.code(a, language='sql')
