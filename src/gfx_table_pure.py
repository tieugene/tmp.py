"""Signal table.
No layout"""
# 1. std
from typing import List
# 2. 3rd
from PyQt5.QtWidgets import QGraphicsItemGroup
# 3. local
from gfx_table_widgets import DataValue, RowItem


class TableItem(QGraphicsItemGroup):
    def __init__(self, dlist: List[DataValue]):
        super().__init__()
        y = 0
        for r, d in enumerate(dlist):
            self.addToGroup(item := RowItem(d))
            item.setY(y)
            y += item.boundingRect().height()
