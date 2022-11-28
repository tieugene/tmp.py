"""Signal table.
LinearLayout version.
Resume: not works same as grid layout
"""
# 1. std
from typing import List
# 2. 3rd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsWidget, QGraphicsLinearLayout
# 3. local
from gfx_table_widgets import DataValue, RowItem, HEADER_TXT, TextItem, LayoutItem


class TableItem(QGraphicsWidget):
    def __init__(self, dlist: List[DataValue]):
        super().__init__()
        lt = QGraphicsLinearLayout(Qt.Vertical, self)
        lt.setSpacing(0)
        lt.addItem(LayoutItem(TextItem(HEADER_TXT)))
        for row, d in enumerate(dlist):
            lt.addItem(LayoutItem(RowItem(d)))
        self.setLayout(lt)
