import sys

import streamlit as st
from loguru import logger
from sqlalchemy import Engine, create_engine, inspect


@st.cache_resource
def init_connection() -> Engine:
    st.session_state['url'] = f'mssql+pyodbc://{st.secrets["database"]["servername"]}' \
                              f'/DbAgilMovingPay?TrustServerCertificate=yes&' \
                              f'driver=ODBC+Driver+{st.secrets["database"]["odbc_driver"]}+for+SQL+Server'
    logger.info(f'URL: {st.session_state["url"]}')
    created_engine = create_engine(st.session_state['url'], echo=True)
    logger.success(f'Conectado ao banco de dados')
    return created_engine


@st.cache_data
def get_tables(_engine: Engine, schema: str = None):
    inspector = inspect(_engine)
    return inspector.get_table_names(schema=schema)
