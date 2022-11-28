"""Signal table.
LinearLayout version.
Resume: not works same as grid layout
"""
# 1. std
from typing import List
# 2. 3rd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsWidget, QGraphicsLinearLayout, QSizePolicy
# 3. local
from gfx_table_widgets import DataValue, LayoutItem, RowItem, TextItem, HEADER_TXT
from gfx_table_zzz import TextGfxWidget


class TableItem(QGraphicsWidget):
    def __init__(self, dlist: List[DataValue]):
        super().__init__()
        lt = QGraphicsLinearLayout(Qt.Vertical, self)
        lt.setSpacing(0)
        lt.addItem(h := TextGfxWidget(HEADER_TXT))
        h.setMinimumHeight(50)
        h.setMaximumHeight(50)
        h.setPreferredHeight(50)
        h.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        # lt.addItem(LayoutItem(TextItem(HEADER_TXT)))
        for row, d in enumerate(dlist):
            lt.addItem(LayoutItem(RowItem(d)))
        # lt.setStretchFactor(lt.itemAt(0), 0)
        self.setLayout(lt)
