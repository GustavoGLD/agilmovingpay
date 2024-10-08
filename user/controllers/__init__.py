import sys

import streamlit as st
from loguru import logger


def filter_secrets(record) -> bool:
    return st.session_state['url'] in record['message']


logger.remove()
logger.add(sys.stdout, level="TRACE", filter=filter_secrets)
logger.add('logs.log', level="TRACE", serialize=True)

import config
from controllers.connection import init_connection, get_tables
from controllers.fetch_data import fetch_data


