"""Signal table.
No layout"""
# 1. std
from typing import List
# 2. 3rd
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsItem
# 3. local
from gfx_table_widgets import DataValue, RectTextItem, W_LABEL, GraphItem


class TableItem(QGraphicsItemGroup):
    class RowItem(QGraphicsItemGroup):
        def __init__(self, d: DataValue, parent: QGraphicsItem = None):
            super().__init__(parent)
            self.addToGroup(RectTextItem(W_LABEL - 1, d[0], d[2]))
            self.addToGroup(graph := GraphItem(d))
            graph.setX(W_LABEL)
            graph.bordered = True

    def __init__(self, dlist: List[DataValue]):
        super().__init__()
        y = 0
        for r, d in enumerate(dlist):
            self.addToGroup(item := self.RowItem(d))
            item.setY(y)
            y += item.boundingRect().height()
