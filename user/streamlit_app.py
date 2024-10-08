"""
$I$COF#2021
"""
import copy
from abc import abstractmethod, ABC
from typing import Union, TypedDict

import streamlit as st
import hydralit_components as hc

from config import pages, APP_NAME
from controllers.update_table import update_table
from models.HydraItem import HydraItem
from streamlit_extras.grid import grid

import streamlit_authenticator as stauth

import yaml
from streamlit_authenticator import Authenticate
from yaml.loader import SafeLoader

st.set_page_config(
    page_title=APP_NAME,
    page_icon='💲',
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)


def remove_metadata(item):
    item = copy.deepcopy(item)
    if isinstance(item, list):
        return [remove_metadata(subitem) for subitem in item]
    elif isinstance(item, dict):
        if 'metadata' in item:
            del item['metadata']
        if 'submenu' in item:
            item['submenu'] = remove_metadata(item['submenu'])
        return item
    else:
        return item


def find_table(items: list[HydraItem], label: str) -> Union[str, None]:
    for item in items:
        if item.get('label') == label:
            return item.get('metadata', {}).get('table')
        if 'submenu' in item:
            result = find_table(item['submenu'], label)
            if result:
                return result
    return None


def main():

    with st.sidebar:
        st.text('↓ Funcionalidades ↓')

        menu_id = hc.nav_bar(
            menu_definition=remove_metadata(pages),
            override_theme={
                'txc_inactive': 'white',
                'menu_background': 'FAFAFA',
                'txc_active': 'white',
                'option_active': 'gray',
                'font-size': '50%'
            },
            first_select=0,
            home_name='Home',
            hide_streamlit_markers=False,
            sticky_nav=False,
            option_menu=False,
            sticky_mode='regular',
        )

    table = find_table(pages, menu_id)
    if table:
        st.info(f'Tabela "{table}"', icon='📋')
        update_table(table)
    else:
        hc.info_card(title='💲 '+APP_NAME, content='☰ Navegue pelo menu para acessar as funcionalidades.')


class User(TypedDict):
    name: str
    password: str


class UserDict(TypedDict):
    usernames: dict[str, User]


class BackLoginMethod(ABC):
    @abstractmethod
    def credentials(self) -> str:
        pass


class Toml(BackLoginMethod):
    @property
    def credentials(self) -> UserDict:
        return st.secrets['credentials'].to_dict()


class Sql(BackLoginMethod):
    @property
    def credentials(self) -> UserDict:
        ...


authenticator = Authenticate(
    Toml().credentials,
    st.secrets['cookie']['name'],
    st.secrets['cookie']['key'],
    st.secrets['cookie']['expiry_days'],
)

name, authentication_status, username = authenticator.login()

if authentication_status:
    st.success(f'👋🙋‍♂️ Bem vindo *{name}*! Login feito com Successo!')
    st.divider()
    main()
    authenticator.logout(location='sidebar')
elif authentication_status is False:
    st.error('❌🔄 Username ou password errado! Tente novamente.')
elif authentication_status is None:
    st.warning('🔑🔒 Escreva seu usuário e senha!')
