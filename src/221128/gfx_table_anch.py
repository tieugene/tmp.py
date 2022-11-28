"""Signal table.
AnchorLayout version.
Resume: ...
"""
# 1. std
from typing import List
# 2. 3rd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsWidget, QSizePolicy, QGraphicsAnchorLayout
# 3. local
from gfx_table_widgets import DataValue, RowItem, TextItem, HEADER_TXT
from gfx_table_zzz import LayoutItem


class TableItem(QGraphicsWidget):
    def __init__(self, dlist: List[DataValue]):
        super().__init__()
        lt = QGraphicsAnchorLayout(self)
        lt.setSpacing(0)
        item = LayoutItem(TextItem(HEADER_TXT))
        item.setMinimumHeight(50)
        item.setMaximumHeight(50)
        item.setPreferredHeight(50)
        item.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        lt.addAnchor(item, Qt.AnchorTop, lt, Qt.AnchorTop)
        for row, d in enumerate(dlist):
            item2 = LayoutItem(RowItem(d))
            lt.addAnchor(item, Qt.AnchorBottom, item2, Qt.AnchorTop)
            item = item2
        lt.addAnchor(item, Qt.AnchorBottom, lt, Qt.AnchorBottom)
        self.setLayout(lt)
