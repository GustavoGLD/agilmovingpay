from typing import Any

import pandas as pd

from models import Borg, BorgName, BorgObj


class SessionState(Borg):
    def __init__(self):
        self.columns_config = BorgName(lambda x: f"{x}_columns_config", dict)
        self.columns_table = BorgName(lambda x: f"{x}_columns_table", dict)
        self.autoincr = BorgName(lambda x: f"{x}_autoincr", list)
        self.tablename = BorgObj('tablename', str)

        self.df_rslt = BorgName(lambda x: f"{x}_df_rslt", pd.DataFrame)
        self.table_df = BorgName(lambda x: f"{x}_table_df", pd.DataFrame)
        self.edited_df = BorgName(lambda x: f"{x}_table_editor", pd.DataFrame)
        self.original_df = BorgName(lambda x: f"{x}_table_original", pd.DataFrame)
        self.original2_df = BorgName(lambda x: f"{x}_table_original2", pd.DataFrame)

        self.values = BorgName(lambda x: f"{x}_values", dict)
        self.last_value = BorgName(lambda x: f'{x}_last_value', dict)

        self.savable = BorgName(lambda x: f"{x}_savable", bool)
        self.saving = BorgName(lambda x: f"{x}_save_btt_key", bool)
        self.table_changes = BorgName(lambda x: f"{x}_table_changes", dict)

        self.query_layouts = BorgName(lambda x: f"{x}_query_layouts", list)
