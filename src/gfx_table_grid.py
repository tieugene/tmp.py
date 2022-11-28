"""Signal table.
GridTable version
Resume:
- lt.setRowFixedHeight works strange
- lt.* not work:
  + setRowStretchFactor
  + setColumnFixedWidth
  + setContentsMargins
  + cell span
Note: now stretch factors depends on (label/graph).boundingRect() ratio
"""
# 1. std
from typing import List
# 2. 3rd
from PyQt5.QtWidgets import QGraphicsWidget, QGraphicsGridLayout
# 3. local
from gfx_table_widgets import W_LABEL, DataValue, RectTextItem, GraphItem, LayoutItem


class TableItem(QGraphicsWidget):
    def __init__(self, dlist: List[DataValue]):
        super().__init__()
        lt = QGraphicsGridLayout(self)
        lt.setSpacing(0)
        for row, d in enumerate(dlist):
            lt.addItem(LayoutItem(RectTextItem(W_LABEL, d[0], d[2])), row, 0)  # A: GridTextItem, B: TextGfxWidget
            lt.addItem(LayoutItem(GraphItem(d)), row, 1)
        # lt.setRowStretchFactor(0, 0)
        self.setLayout(lt)
