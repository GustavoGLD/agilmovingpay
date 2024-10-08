from typing import TypedDict, Literal


class MetaData(TypedDict):
    table: str
    func: Literal['update_table', 'create_table', 'delete_table']


class HydraItem(TypedDict, total=False):
    icon: str
    label: str
    metadata: MetaData
    submenu: list["HydraItem"]