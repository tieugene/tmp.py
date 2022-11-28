"""Signal table.
GridTable version.
Resume: not works same as grid layout
"""
# 1. std
from typing import List
# 2. 3rd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsWidget, QGraphicsLinearLayout
# 3. local
from gfx_table_widgets import DataValue, LayoutItem, RowItem


class TableItem(QGraphicsWidget):
    def __init__(self, dlist: List[DataValue]):
        super().__init__()
        lt = QGraphicsLinearLayout(Qt.Vertical, self)
        lt.setSpacing(0)
        for row, d in enumerate(dlist):
            lt.addItem(LayoutItem(RowItem(d)))
        # lt.setStretchFactor(lt.itemAt(0), 0)
        self.setLayout(lt)
